from lxml import etree
from typing import List, Dict, Any
from decimal import Decimal
from datetime import datetime
from app.core.config import settings
import io

class XmlGeneratorService:
    @staticmethod
    def formatar_valor(value: Any) -> str:
        """Converte valores para o padrão brasileiro de string com vírgula, com arredondamento de 2 casas."""
        try:
            if value is None or value == "":
                return "0,00"
            val = round(float(value), 2)
            return f"{val:.2f}".replace('.', ',')
        except:
            return "0,00"

    @staticmethod
    def gerar_lote_xml(notas_enriquecidas: List[Dict[str, Any]], data_competencia: str) -> tuple[bytes, List[Dict[str, Any]]]:
        """
        Gera o Lote de RPS no padrão Sdt_ProcessarpsIn (Prefeitura de Caieiras).
        Retorna (bytes do XML, lista de alertas de campos em branco).
        """
        warnings = []
        
        # Ano e Mês da competência
        try:
            ano_comp, mes_comp = data_competencia.split("-")
        except:
            ano_comp, mes_comp = str(datetime.now().year), f"{datetime.now().month:02d}"

        # Root: Sdt_ProcessarpsIn
        root = etree.Element("Sdt_ProcessarpsIn", nsmap={None: "NFe"})
        
        # 1. Login
        login = etree.SubElement(root, "Login")
        etree.SubElement(login, "CodigoUsuario").text = settings.CODIGO_USUARIO
        etree.SubElement(login, "CodigoContribuinte").text = settings.CODIGO_CONTRIBUINTE

        # 2. SDTRPS
        sdtrps = etree.SubElement(root, "SDTRPS")
        etree.SubElement(sdtrps, "Ano").text = ano_comp
        etree.SubElement(sdtrps, "Mes").text = mes_comp
        etree.SubElement(sdtrps, "CPFCNPJ").text = settings.PRESTADOR_CNPJ
        
        # Busca datas min/max do lote conforme Colab
        datas_emissao = []
        for nota in notas_enriquecidas:
            dt = nota.get("DtEmi")
            if dt:
                if isinstance(dt, datetime):
                    datas_emissao.append(dt)
                else:
                    try:
                        datas_emissao.append(datetime.fromisoformat(str(dt).replace('Z', '+00:00')))
                    except:
                        pass
        
        try:
            if datas_emissao:
                data_min = min(datas_emissao).strftime('%d/%m/%Y')
                data_max = max(datas_emissao).strftime('%d/%m/%Y')
            else:
                data_min = f"01/{mes_comp}/{ano_comp}"
                data_max = f"30/{mes_comp}/{ano_comp}"
        except:
            data_min = f"01/{mes_comp}/{ano_comp}"
            data_max = f"30/{mes_comp}/{ano_comp}"
        
        etree.SubElement(sdtrps, "DTIni").text = data_min
        etree.SubElement(sdtrps, "DTFin").text = data_max
        etree.SubElement(sdtrps, "TipoTrib").text = "1"
        
        # Tags vazias conforme Colab
        for t in ["DtAdeSN", "AlqIssSN_IP", "RegApTribSN", "TribTpSusp", "TribProcSusp"]:
            etree.SubElement(sdtrps, t)
            
        etree.SubElement(sdtrps, "Versao").text = "4.00"

        # 3. Reg20 (Lista de RPS)
        reg20_parent = etree.SubElement(sdtrps, "Reg20")

        total_iss = 0.0
        total_servicos = 0.0
        qtd_notas = 0
        qtd_reg40 = 0

        for nota in notas_enriquecidas:
            num_rps_raw = str(nota.get("NumRps", "")).strip()
            if not num_rps_raw: continue
            
            num_rps = "".join(filter(str.isdigit, num_rps_raw))
            
            raw_cnpj = str(nota.get("CpfCnpTom", "")).strip()
            if str(raw_cnpj).lower() == 'nan': raw_cnpj = ""
            num_cnpj = "".join(filter(str.isdigit, raw_cnpj))
            cnpj_final = num_cnpj if num_cnpj else raw_cnpj
            

            # Validação de campos obrigatórios (Inteligência contra campos brancos)
            campos_obrigatorios = {
                "RazSocTom": "Razão Social",
                "LogTom": "Logradouro (Endereço)",
                "NumEndTom": "Número do Endereço",
                "BairroTom": "Bairro do Tomador",
                "MunTom": "Município",
                "CepTom": "CEP"
            }
            
            for field, label in campos_obrigatorios.items():
                val = str(nota.get(field, "")).strip()
                if not val or val.upper() in ["NAO INFORMADO", "00000000", "NAN", "NONE"]:
                    warnings.append({
                        "rps": num_rps,
                        "cnpj": cnpj_final,
                        "razao_social": str(nota.get("RazSocTom", "Não Informado")),
                        "campo": label,
                        "field": field,
                        "valor_atual": val or "Vazio"
                    })

            # Item da Nota
            item = etree.SubElement(reg20_parent, "Reg20Item")
            
            etree.SubElement(item, "TipoNFS").text = "RPS"
            etree.SubElement(item, "NumRps").text = num_rps
            etree.SubElement(item, "SerRps").text = "E"
            
            dt_emissao = nota.get("DtEmi")
            if isinstance(dt_emissao, datetime):
                dt_str = dt_emissao.strftime("%d/%m/%Y")
            else:
                try:
                    dt_obj = datetime.fromisoformat(str(dt_emissao).replace('Z', '+00:00'))
                    dt_str = dt_obj.strftime("%d/%m/%Y")
                except:
                    dt_str = data_min

            etree.SubElement(item, "DtEmi").text = dt_str
            etree.SubElement(item, "RetFonte").text = "NAO"
            etree.SubElement(item, "CodSrv").text = settings.COD_SERVICO_FIXO
            etree.SubElement(item, "DiscrSrv").text = settings.DISCRIMINACAO_FIXA
            
            # Valores
            try:
                v_nfs_raw = float(nota.get("VlNFS_Calculado", 0.0))
                v_iss_raw = float(nota.get("VlIss_Calculado", 0.0))
                
                v_nfs_final = round(v_nfs_raw, 2)
                v_iss_final = round(v_iss_raw, 2)
            except:
                v_nfs_final = 0.0
                v_iss_final = 0.0

            total_servicos += v_nfs_final
            total_iss += v_iss_final
            qtd_notas += 1

            etree.SubElement(item, "VlNFS").text = XmlGeneratorService.formatar_valor(v_nfs_final)
            etree.SubElement(item, "VlDed").text = "0,00"
            etree.SubElement(item, "DiscrDed")
            etree.SubElement(item, "VlBasCalc").text = XmlGeneratorService.formatar_valor(v_nfs_final)
            etree.SubElement(item, "AlqIss").text = "2,00"
            etree.SubElement(item, "VlIss").text = XmlGeneratorService.formatar_valor(v_iss_final)
            etree.SubElement(item, "VlIssRet").text = "0,00"
            
            # Tomador
            etree.SubElement(item, "CpfCnpTom").text = "".join(filter(str.isdigit, str(nota.get("CpfCnpTom", ""))))
            etree.SubElement(item, "RazSocTom").text = str(nota.get("RazSocTom", ""))[:100]

            # Endereço
            etree.SubElement(item, "TipoLogtom").text = str(nota.get("TipoLogtom", "RUA")).strip() or "RUA"
            etree.SubElement(item, "LogTom").text = str(nota.get("LogTom", "")).strip()
            etree.SubElement(item, "NumEndTom").text = str(nota.get("NumEndTom", "S/N")).strip()
            etree.SubElement(item, "ComplEndTom")
            etree.SubElement(item, "BairroTom").text = str(nota.get("BairroTom", "")).strip()
            etree.SubElement(item, "MunTom").text = str(nota.get("MunTom", "SAO PAULO")).strip().upper() or "SAO PAULO"
            etree.SubElement(item, "SiglaUFTom").text = str(nota.get("SiglaUFTom", "SP")).strip().upper() or "SP"
            etree.SubElement(item, "CepTom").text = "".join(filter(str.isdigit, str(nota.get("CepTom", ""))))
            etree.SubElement(item, "Telefone")
            etree.SubElement(item, "InscricaoMunicipal")
            
            # Local Prestação (Vazios conforme Colab)
            for t in ["TipoLogLocPre", "LogLocPre", "NumEndLocPre", "ComplEndLocPre", "BairroLocPre", "MunLocPre", "SiglaUFLocpre", "CepLocPre"]:
                etree.SubElement(item, t)
            
            etree.SubElement(item, "Email1").text = "xml@processamento.com.br"
            etree.SubElement(item, "Email2")
            etree.SubElement(item, "Email3")

            # 4. Reg40
            reg40 = etree.SubElement(item, "Reg40")
            r1 = etree.SubElement(reg40, "Reg40Item")
            etree.SubElement(r1, "SiglaCpoAdc").text = "SRV_NBS"
            etree.SubElement(r1, "ConteudoCpoAdc").text = "".join(filter(str.isdigit, settings.PADRAO_COD_NBS))
            r2 = etree.SubElement(reg40, "Reg40Item")
            etree.SubElement(r2, "SiglaCpoAdc").text = "SRV_CTN"
            etree.SubElement(r2, "ConteudoCpoAdc").text = "".join(filter(str.isdigit, settings.PADRAO_COD_CTN))
            qtd_reg40 += 2

            # 5. Reg60_RTC
            reg60 = etree.SubElement(item, "Reg60_RTC")
            etree.SubElement(reg60, "Finalidade").text = "0"
            etree.SubElement(reg60, "IndConsFin").text = "NAO"
            etree.SubElement(reg60, "IndDest").text = "SIM"
            etree.SubElement(reg60, "IndOpeOne").text = "SIM"
            etree.SubElement(reg60, "IndCodOpe").text = "100301"
            etree.SubElement(reg60, "VlReeRepRes").text = "0,00"
            
            g1 = etree.SubElement(reg60, "gIBSCBS")
            etree.SubElement(g1, "CST").text = "000"
            etree.SubElement(g1, "CClassTrib").text = "000001"
            etree.SubElement(g1, "CCodCredPres").text = "12"
            
            g2 = etree.SubElement(reg60, "gTribReg")
            etree.SubElement(g2, "CST").text = "000"
            etree.SubElement(g2, "CClassTrib").text = "000001"
            
            g3 = etree.SubElement(reg60, "gDif")
            etree.SubElement(g3, "PDifUF").text = "0,00"
            etree.SubElement(g3, "PDifMun").text = "0,10"
            etree.SubElement(g3, "PDifCBS").text = "0,90"

        # 6. Reg90 (Rodapé)
        reg90 = etree.SubElement(sdtrps, "Reg90")
        etree.SubElement(reg90, "QtdRegNormal").text = str(qtd_notas)
        etree.SubElement(reg90, "ValorNFS").text = XmlGeneratorService.formatar_valor(total_servicos)
        etree.SubElement(reg90, "ValorISS").text = XmlGeneratorService.formatar_valor(total_iss)
        etree.SubElement(reg90, "ValorDed").text = "0,00"
        etree.SubElement(reg90, "ValorIssRetTom").text = "0,00"
        etree.SubElement(reg90, "QtdReg30").text = "0"
        etree.SubElement(reg90, "ValorTributos").text = "0,00"
        etree.SubElement(reg90, "QtdReg40").text = str(qtd_reg40)
        etree.SubElement(reg90, "QtdReg50").text = "0"

        # Finalização com UTF-8 e Declaração XML
        xml_bytes = etree.tostring(root, encoding="utf-8", xml_declaration=True, pretty_print=True)
        return xml_bytes, warnings
