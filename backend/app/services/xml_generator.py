from lxml import etree
from typing import List, Dict, Any
from decimal import Decimal
from datetime import datetime
from app.core.config import settings
import io

class XmlGeneratorService:
    @staticmethod
    def format_comma(value: Any) -> str:
        """Converte valores para o padrão brasileiro de string com vírgula."""
        try:
            if value is None or value == "":
                return "0,00"
            num = Decimal(str(value))
            return f"{num:.2f}".replace(".", ",")
        except:
            return "0,00"

    @staticmethod
    def gerar_lote_xml(notas_enriquecidas: List[Dict[str, Any]], data_competencia: str) -> bytes:
        """
        Gera o Lote de RPS no padrão Sdt_ProcessarpsIn (Prefeitura de Caieiras).
        data_competencia no formato YYYY-MM
        """
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
        
        # DTIni/DTFin - Usando padrão do modelo (primeiro e último dia ou fixo se preferir)
        # No modelo colab estava 30/03/2026. Vamos usar a competência.
        data_ini = f"01/{mes_comp}/{ano_comp}"
        # Simples aproximação do fim do mês
        data_fin = f"30/{mes_comp}/{ano_comp}" if mes_comp != "02" else f"28/{mes_comp}/{ano_comp}"
        
        etree.SubElement(sdtrps, "DTIni").text = data_ini
        etree.SubElement(sdtrps, "DTFin").text = data_fin
        etree.SubElement(sdtrps, "TipoTrib").text = "1"
        etree.SubElement(sdtrps, "DtAdeSN").text = ""
        etree.SubElement(sdtrps, "AlqIssSN_IP").text = ""
        etree.SubElement(sdtrps, "RegApTribSN").text = ""
        etree.SubElement(sdtrps, "TribTpSusp").text = ""
        etree.SubElement(sdtrps, "TribProcSusp").text = ""
        etree.SubElement(sdtrps, "Versao").text = "4.00"

        # 3. Reg20 (Lista de RPS)
        reg20_parent = etree.SubElement(sdtrps, "Reg20")

        total_iss = Decimal("0.00")
        total_servicos = Decimal("0.00")
        qtd_notas = len(notas_enriquecidas)

        for nota in notas_enriquecidas:
            # Item da Nota
            item = etree.SubElement(reg20_parent, "Reg20Item")
            
            etree.SubElement(item, "TipoNFS").text = "RPS"
            etree.SubElement(item, "NumRps").text = str(nota.get("NumRps", ""))
            etree.SubElement(item, "SerRps").text = "E"  # Padrão conforme modelo Colab
            
            # Data Emissão (DD/MM/YYYY)
            dt_emissao = nota.get("DtEmi", "")
            if isinstance(dt_emissao, datetime):
                dt_str = dt_emissao.strftime("%d/%m/%Y")
            else:
                # Tentar converter se for string ISO
                try:
                    dt_obj = datetime.fromisoformat(str(dt_emissao).replace('Z', '+00:00'))
                    dt_str = dt_obj.strftime("%d/%m/%Y")
                except:
                    dt_str = str(dt_emissao)

            etree.SubElement(item, "DtEmi").text = dt_str
            etree.SubElement(item, "RetFonte").text = "NAO"
            etree.SubElement(item, "CodSrv").text = settings.COD_SERVICO_FIXO
            etree.SubElement(item, "DiscrSrv").text = settings.DISCRIMINACAO_FIXA
            
            v_nfs = Decimal(str(nota.get("VlNFS_Calculado", 0.0)))
            v_iss = Decimal(str(nota.get("VlIss_Calculado", 0.0)))
            total_servicos += v_nfs
            total_iss += v_iss

            etree.SubElement(item, "VlNFS").text = XmlGeneratorService.format_comma(v_nfs)
            etree.SubElement(item, "VlDed").text = "0,00"
            etree.SubElement(item, "DiscrDed").text = ""
            etree.SubElement(item, "VlBasCalc").text = XmlGeneratorService.format_comma(v_nfs)
            etree.SubElement(item, "AlqIss").text = "2,00"
            etree.SubElement(item, "VlIss").text = XmlGeneratorService.format_comma(v_iss)
            etree.SubElement(item, "VlIssRet").text = "0,00"
            
            etree.SubElement(item, "CpfCnpTom").text = str(nota.get("CpfCnpTom", ""))
            etree.SubElement(item, "RazSocTom").text = str(nota.get("RazSocTom", "")).upper()
            etree.SubElement(item, "TipoLogtom").text = str(nota.get("TipoLogtom", "RUA")).upper()
            etree.SubElement(item, "LogTom").text = str(nota.get("LogTom", "")).upper()
            etree.SubElement(item, "NumEndTom").text = str(nota.get("NumEndTom", "S/N"))
            etree.SubElement(item, "ComplEndTom").text = ""
            etree.SubElement(item, "BairroTom").text = str(nota.get("BairroTom", "")).upper()
            etree.SubElement(item, "MunTom").text = str(nota.get("MunTom", "")).upper()
            etree.SubElement(item, "SiglaUFTom").text = str(nota.get("SiglaUFTom", "SP")).upper()
            etree.SubElement(item, "CepTom").text = str(nota.get("CepTom", ""))
            etree.SubElement(item, "Telefone").text = ""
            etree.SubElement(item, "InscricaoMunicipal").text = ""
            
            # Local Prestação
            etree.SubElement(item, "TipoLogLocPre").text = ""
            etree.SubElement(item, "LogLocPre").text = ""
            etree.SubElement(item, "NumEndLocPre").text = ""
            etree.SubElement(item, "ComplEndLocPre").text = ""
            etree.SubElement(item, "BairroLocPre").text = ""
            etree.SubElement(item, "MunLocPre").text = ""
            etree.SubElement(item, "SiglaUFLocpre").text = ""
            etree.SubElement(item, "CepLocPre").text = ""
            
            # Email (Fixo conforme modelo ou vazio)
            etree.SubElement(item, "Email1").text = "xml@processamento.com.br"
            etree.SubElement(item, "Email2").text = ""
            etree.SubElement(item, "Email3").text = ""

            # 4. Reg40
            reg40 = etree.SubElement(item, "Reg40")
            
            # NBS Item
            r40_nbs = etree.SubElement(reg40, "Reg40Item")
            etree.SubElement(r40_nbs, "SiglaCpoAdc").text = "SRV_NBS"
            etree.SubElement(r40_nbs, "ConteudoCpoAdc").text = settings.PADRAO_COD_NBS
            
            # CTN Item
            r40_ctn = etree.SubElement(reg40, "Reg40Item")
            etree.SubElement(r40_ctn, "SiglaCpoAdc").text = "SRV_CTN"
            etree.SubElement(r40_ctn, "ConteudoCpoAdc").text = settings.PADRAO_COD_CTN

            # 5. Reg60_RTC (Impostos e Tributação Complementar)
            reg60 = etree.SubElement(item, "Reg60_RTC")
            etree.SubElement(reg60, "Finalidade").text = "0"
            etree.SubElement(reg60, "IndConsFin").text = "NAO"
            etree.SubElement(reg60, "IndDest").text = "SIM"
            etree.SubElement(reg60, "IndOpeOne").text = "SIM"
            etree.SubElement(reg60, "IndCodOpe").text = "100301"
            etree.SubElement(reg60, "VlReeRepRes").text = "0,00"
            
            gibs = etree.SubElement(reg60, "gIBSCBS")
            etree.SubElement(gibs, "CST").text = "000"
            etree.SubElement(gibs, "CClassTrib").text = "000001"
            etree.SubElement(gibs, "CCodCredPres").text = "12"
            
            gtrib = etree.SubElement(reg60, "gTribReg")
            etree.SubElement(gtrib, "CST").text = "000"
            etree.SubElement(gtrib, "CClassTrib").text = "000001"
            
            gdif = etree.SubElement(reg60, "gDif")
            etree.SubElement(gdif, "PDifUF").text = "0,00"
            etree.SubElement(gdif, "PDifMun").text = "0,10"
            etree.SubElement(gdif, "PDifCBS").text = "0,90"

        # 6. Reg90 (Rodapé de Totais)
        reg90 = etree.SubElement(sdtrps, "Reg90")
        etree.SubElement(reg90, "QtdRegNormal").text = str(qtd_notas)
        etree.SubElement(reg90, "ValorNFS").text = XmlGeneratorService.format_comma(total_servicos)
        etree.SubElement(reg90, "ValorISS").text = XmlGeneratorService.format_comma(total_iss)
        etree.SubElement(reg90, "ValorDed").text = "0,00"
        etree.SubElement(reg90, "ValorIssRetTom").text = "0,00"
        etree.SubElement(reg90, "QtdReg30").text = "0"
        etree.SubElement(reg90, "ValorTributos").text = "0,00"
        etree.SubElement(reg90, "QtdReg40").text = str(qtd_notas * 2) # 2 subitens Reg40 por nota
        etree.SubElement(reg90, "QtdReg50").text = "0"

        # Finalização com UTF-8 e Declaração XML
        return etree.tostring(root, encoding="utf-8", xml_declaration=True, pretty_print=True)
