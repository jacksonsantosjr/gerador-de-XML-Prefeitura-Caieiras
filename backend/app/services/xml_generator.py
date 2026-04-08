from lxml import etree
from typing import List, Dict, Any
from decimal import Decimal
from datetime import datetime
from app.core.config import settings
import io

class XmlGeneratorService:
    @staticmethod
    def gerar_lote_xml(notas_enriquecidas: List[Dict[str, Any]], data_competencia: str) -> bytes:
        """
        Recebe a lista de dicionários já processada, enriquecida com endereços e impostos,
        e gera o Lote de RPS em sintaxe XML UTF-8.
        data_competencia no formato YYYY-MM
        """
        # Elemento root padrão para NFe (Pode ter variações locais, mantendo o padrão ABRASF base)
        root = etree.Element("NFe", nsmap={None: "http://www.abrasf.org.br/ABRASF/arquivos/nfse.xsd"})
        
        # Reg10 (Cabeçalho do Contribuinte)
        cabecalho = etree.SubElement(root, "Cabecalho")
        etree.SubElement(cabecalho, "CodigoUsuario").text = settings.CODIGO_USUARIO
        etree.SubElement(cabecalho, "CodigoContribuinte").text = settings.CODIGO_CONTRIBUINTE
        etree.SubElement(cabecalho, "CnpjPrestador").text = settings.PRESTADOR_CNPJ
        etree.SubElement(cabecalho, "DataCompetencia").text = data_competencia

        total_iss = Decimal("0.00")
        total_servicos = Decimal("0.00")
        total_notas = len(notas_enriquecidas)

        # Iterar sobre cada nota processada
        for nota in notas_enriquecidas:
            num_rps = nota.get("NumRps", "")
            data_emissao = nota.get("DtEmi", "")
            
            # Formata data para ISO
            try:
                if isinstance(data_emissao, datetime):
                    dt_str = data_emissao.strftime("%Y-%m-%d")
                else:
                    dt_str = str(data_emissao).split()[0]
            except:
                dt_str = str(data_emissao)

            v_nfs = nota.get("VlNFS_Calculado", Decimal("0.00"))
            v_iss = nota.get("VlIss_Calculado", Decimal("0.00"))
            
            total_servicos += v_nfs
            total_iss += v_iss
            
            # --- Reg20 (Dados Principais do RPS) ---
            reg20 = etree.SubElement(root, "Reg20")
            etree.SubElement(reg20, "TipoDocumento").text = "RPS"
            etree.SubElement(reg20, "NumeroRPS").text = str(num_rps)
            etree.SubElement(reg20, "Serie").text = "A" # Fixo ou dinâmico pela UI
            etree.SubElement(reg20, "DataEmissao").text = dt_str
            etree.SubElement(reg20, "SituacaoRPS").text = "N" # Normal
            etree.SubElement(reg20, "ValorServicos").text = f"{v_nfs:.2f}"
            etree.SubElement(reg20, "ValorDeducoes").text = "0.00"
            etree.SubElement(reg20, "BaseCalculo").text = f"{v_nfs:.2f}"
            etree.SubElement(reg20, "Aliquota").text = "2.00" # 2%
            etree.SubElement(reg20, "ValorISS").text = f"{v_iss:.2f}"
            etree.SubElement(reg20, "IssRetido").text = "2" # 1=Sim, 2=Não
            etree.SubElement(reg20, "Discriminacao").text = settings.DISCRIMINACAO_FIXA

            # Tomador
            tomador = etree.SubElement(reg20, "Tomador")
            etree.SubElement(tomador, "CpfCnpj").text = str(nota.get("CpfCnpTom", ""))
            etree.SubElement(tomador, "RazaoSocial").text = str(nota.get("RazSocTom", ""))
            
            end = etree.SubElement(tomador, "Endereco")
            etree.SubElement(end, "TipoLogradouro").text = str(nota.get("TipoLogtom", "RUA"))
            etree.SubElement(end, "Logradouro").text = str(nota.get("LogTom", "Nao Informado"))
            etree.SubElement(end, "NumeroEndereco").text = str(nota.get("NumEndTom", "S/N"))
            etree.SubElement(end, "Bairro").text = str(nota.get("BairroTom", ""))
            etree.SubElement(end, "Cidade").text = str(nota.get("MunTom", ""))
            etree.SubElement(end, "UF").text = str(nota.get("SiglaUFTom", ""))
            etree.SubElement(end, "CEP").text = str(nota.get("CepTom", ""))

            # --- Reg40 (Serviço CTN) ---
            reg40 = etree.SubElement(reg20, "Reg40")
            etree.SubElement(reg40, "CodigoServico").text = settings.COD_SERVICO_FIXO
            etree.SubElement(reg40, "CodigoCTN").text = settings.PADRAO_COD_CTN
            etree.SubElement(reg40, "CodigoNBS").text = settings.PADRAO_COD_NBS

            # --- Reg60_RTC (Impostos Retidos/Federais se houver) ---
            reg60 = etree.SubElement(reg20, "Reg60_RTC")
            etree.SubElement(reg60, "RetidoPIS").text = "0.00"
            etree.SubElement(reg60, "RetidoCOFINS").text = "0.00"
            etree.SubElement(reg60, "RetidoINSS").text = "0.00"
            etree.SubElement(reg60, "RetidoIR").text = "0.00"
            etree.SubElement(reg60, "RetidoCSLL").text = "0.00"

        # --- Reg90 (Rodapé - Totais do Lote) ---
        reg90 = etree.SubElement(root, "Reg90")
        etree.SubElement(reg90, "QtdNotas").text = str(total_notas)
        etree.SubElement(reg90, "TotalServicos").text = f"{total_servicos:.2f}"
        etree.SubElement(reg90, "TotalDeducoes").text = "0.00"
        etree.SubElement(reg90, "TotalISS").text = f"{total_iss:.2f}"

        # Montagem do Arquivo XML Final com encoding correto
        xml_str = etree.tostring(root, encoding="utf-8", xml_declaration=True, pretty_print=True)
        return xml_str
