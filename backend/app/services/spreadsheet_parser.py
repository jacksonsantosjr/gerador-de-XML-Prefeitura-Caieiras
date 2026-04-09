import pandas as pd
from typing import List, Dict, Any
from io import BytesIO

class SpreadsheetParser:
    # Mapeamento do Layout Bruto do ERP
    # "Nº do Movimento" > "NumRps"
    # "Data Emissão" > "DtEmi" 
    # "Valor do Documento" > "VlNFS"
    # "CPF/CNPJ" > "CpfCnpTom"
    # "Razão Social" > "RazSocTom"
    
    EXPECTED_COLUMNS = {
        "Nº do Movimento": "NumRps",
        "Data Emissão": "DtEmi",
        "Valor do Documento": "VlNFS",
        "CPF/CNPJ": "CpfCnpTom",
        "Razão Social": "RazSocTom"
    }

    @staticmethod
    def parse_file(file_content: bytes, filename: str) -> List[Dict[str, Any]]:
        """Lê o arquivo do ERP em memória e converte nas 5 colunas base."""
        try:
            if filename.lower().endswith(".csv"):
                df = pd.read_csv(BytesIO(file_content), sep=None, engine='python')
            else:
                df = pd.read_excel(BytesIO(file_content))
                
            # Identificadores problemáticos que as vezes vem nas planilhas e dão erro de codificação
            colunas_reais = list(df.columns)
            
            # Buscando as colunas primeiro por match EXATO (prioridade máxima)
            colunas_mapeadas = {}
            alvos_encontrados = set()
            
            # 1. Busca Exata (ERP layout mapping)
            for col in colunas_reais:
                str_col = str(col).strip().upper()
                if str_col in ["Nº DO MOVIMENTO", "N DO MOVIMENTO", "NUMERO DO MOVIMENTO"]:
                    target = "NumRps"
                elif str_col in ["DATA EMISSÃO", "DATA EMISSAO"]:
                    target = "DtEmi"
                elif str_col in ["VALOR DO DOCUMENTO", "VALOR DOCUMENTO"]:
                    target = "VlNFS"
                elif str_col in ["CPF/CNPJ", "CPF / CNPJ", "CPF/CNPJ CLI/FOR"]:
                    target = "CpfCnpTom"
                elif str_col in ["RAZÃO SOCIAL", "RAZAO SOCIAL", "RAZAO SOCIAL CLI/FOR"]:
                    target = "RazSocTom"
                else:
                    target = None
                    
                if target and target not in alvos_encontrados:
                    colunas_mapeadas[col] = target
                    alvos_encontrados.add(target)
            
            # 2. Busca flexível apenas para os que faltaram (fallback)
            for col in colunas_reais:
                str_col = str(col).strip().upper()
                target = None
                
                if "NumRps" not in alvos_encontrados and "N" in str_col and "MOVIMENTO" in str_col:
                    target = "NumRps"
                elif "DtEmi" not in alvos_encontrados and "DATA" in str_col and "EMISS" in str_col:
                    target = "DtEmi"
                elif "VlNFS" not in alvos_encontrados and "VALOR" in str_col and "DOCUMENTO" in str_col:
                    target = "VlNFS"
                elif "CpfCnpTom" not in alvos_encontrados and "CPF" in str_col and "CNPJ" in str_col:
                    target = "CpfCnpTom"
                elif "RazSocTom" not in alvos_encontrados and "RAZ" in str_col and "SOCIAL" in str_col:
                    target = "RazSocTom"
                
                if target and target not in alvos_encontrados:
                    colunas_mapeadas[col] = target
                    alvos_encontrados.add(target)
            
            # Renomeia as colunas identificadas
            df.rename(columns=colunas_mapeadas, inplace=True)
            
            # Filtra apenas o que importa (descarta lixo)
            colunas_finais = ["NumRps", "DtEmi", "VlNFS", "CpfCnpTom", "RazSocTom"]
            for c in colunas_finais:
                if c not in df.columns:
                    raise ValueError(f"Coluna alvo obrigatória não encontrada/identificada: {c}")
                    
            # Garante que pegamos apenas uma Series mesmo se houver duplicatas remanescentes no nome
            df_cleaned = pd.DataFrame()
            for col in colunas_finais:
                # Se for DataFrame (múltiplas colunas com o mesmo nome), pega a primeira
                if isinstance(df[col], pd.DataFrame):
                    df_cleaned[col] = df[col].iloc[:, 0]
                else:
                    df_cleaned[col] = df[col]
            
            # Retira linhas onde NumRps é vazio (provável totalizador ou lixo)
            df_cleaned.dropna(subset=["NumRps", "CpfCnpTom"], inplace=True)
            
            # Tratamento primário (limpar zeros e espaços)
            df_cleaned["NumRps"] = df_cleaned["NumRps"].astype(str).str.replace(".0", "", regex=False).str.strip()
            df_cleaned["CpfCnpTom"] = df_cleaned["CpfCnpTom"].astype(str).str.strip()
            
            return df_cleaned.to_dict(orient="records")
            
        except Exception as e:
            raise ValueError(f"Falha ao ler o arquivo ERP: {str(e)}")
