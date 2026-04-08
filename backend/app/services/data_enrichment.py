from sqlalchemy.orm import Session
from app.models.tomador import Tomador
from app.services.brasil_api import BrasilAPIService
from typing import List, Dict, Any, Tuple
import asyncio
import logging

logger = logging.getLogger(__name__)

class EnrichmentService:
    @staticmethod
    async def enrich_and_verify_tomadores(db: Session, raw_rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Analisa a lista brural extraída do ERP.
        Para cada linha, verifica se o 'CpfCnpTom' existe no DB (Supabase).
        Se não existir (e for CNPJ), chama a BrasilAPI.
        Retorna as notas enriquecidas prontas para o Gerador XML, e um relátorio de match.
        """
        enriched_rows = []
        stats = {
            "total_notas": len(raw_rows),
            "tomadores_existentes": 0,
            "tomadores_novos_brasilapi": 0,
            "tomadores_nao_encontrados": 0
        }

        # Extrair CNPJs únicos do lote para minimizar chamadas do BD
        cnpjs_no_lote = set()
        for r in raw_rows:
            raw_doc = str(r.get("CpfCnpTom", "")).strip()
            clean_doc = ''.join(filter(str.isdigit, raw_doc))
            if clean_doc:
                cnpjs_no_lote.add(clean_doc)

        # Buscar todos os Tomadores já existentes (Em massa para alta performance)
        tomadores_db = db.query(Tomador).filter(Tomador.cnpj.in_(cnpjs_no_lote)).all()
        tomadores_map = {t.cnpj: t for t in tomadores_db}
        
        # Identificar quem está faltando
        faltantes = cnpjs_no_lote - set(tomadores_map.keys())
        
        # Se houver CNPJs faltantes, vamos rodar chamadas assíncronas concorrentes para a BrasilAPI!
        if faltantes:
            logger.info(f"{len(faltantes)} clientes não localizados no banco. Acionando BrasilAPI...")
            
            # Chama a Brasil API concorrentemente para máxima velocidade
            tasks = [BrasilAPIService.fetch_cnpj_data(cnpj) for cnpj in faltantes if len(cnpj) == 14]
            resultados_api = await asyncio.gather(*tasks)
            
            novos_tomadores_db = []
            for res in resultados_api:
                if res is not None:
                    # Achou na Brasil API! Vamos criar no nosso Supabase
                    novo = Tomador(
                        cnpj=res["cnpj"],
                        razao_social=res["razao_social"],
                        tipo_logradouro=res["tipo_logradouro"],
                        logradouro=res["logradouro"],
                        numero=res["numero"],
                        complemento=res["complemento"],
                        bairro=res["bairro"],
                        municipio=res["municipio"],
                        uf=res["uf"],
                        cep=res["cep"]
                    )
                    novos_tomadores_db.append(novo)
                    tomadores_map[novo.cnpj] = novo # Atualiza o mapa na memória
                    stats["tomadores_novos_brasilapi"] += 1

            if novos_tomadores_db:
                # Salva os novos no banco definitivamente
                db.add_all(novos_tomadores_db)
                db.commit()

        # Agora, montamos as linhas finais enriquecidas!
        for r in raw_rows:
            raw_doc = str(r.get("CpfCnpTom", "")).strip()
            clean_doc = ''.join(filter(str.isdigit, raw_doc))
            tomador = tomadores_map.get(clean_doc)

            enriched = dict(r) # Cópia da linha do ERP
            
            if tomador:
                if clean_doc in faltantes:
                    # Ele foi inserido agora mesmo
                    pass
                else:
                    stats["tomadores_existentes"] += 1
                    
                # Injeta os dados limpos do banco para a linha do XML
                enriched["CpfCnpTom"] = tomador.cnpj
                enriched["RazSocTom"] = tomador.razao_social
                enriched["TipoLogtom"] = tomador.tipo_logradouro or ""
                enriched["LogTom"] = tomador.logradouro or ""
                enriched["NumEndTom"] = tomador.numero or ""
                enriched["BairroTom"] = tomador.bairro or ""
                enriched["MunTom"] = tomador.municipio or ""
                enriched["SiglaUFTom"] = tomador.uf or ""
                enriched["CepTom"] = tomador.cep or ""
            else:
                stats["tomadores_nao_encontrados"] += 1
                # O XML Core terá que decidir se gera XML com falta de endereço, 
                # ou se a UI bloqueia a nota. No frontend esse status volta para o usuário avisando e travando.
                enriched["MISSING_ADDRESS"] = True

            enriched_rows.append(enriched)

        return enriched_rows, stats
