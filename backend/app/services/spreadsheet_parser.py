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
            
            # Buscando de forma flexível as colunas alvo
            # Porque no ERP às vezes vem "Data Emisso" ou "N do Movimento" (erro de acento)
            colunas_mapeadas = {}
            for col in colunas_reais:
                str_col = str(col).strip().upper()
                if "N" in str_col and "MOVIMENTO" in str_col:
                    colunas_mapeadas[col] = "NumRps"
                elif "DATA" in str_col and "EMISS" in str_col:
                    colunas_mapeadas[col] = "DtEmi"
                elif "VALOR DO DOCUMENTO" in str_col or "VALOR" in str_col and "DOCUMENTO" in str_col:
                    colunas_mapeadas[col] = "VlNFS"
                elif "CPF" in str_col and "CNPJ" in str_col:
                    colunas_mapeadas[col] = "CpfCnpTom"
                elif "RAZ" in str_col and "SOCIAL" in str_col:
                    colunas_mapeadas[col] = "RazSocTom"
            
            # Renomeia as lidas
            df.rename(columns=colunas_mapeadas, inplace=True)
            
            # Filtra apenas o que importa (descarta lixo)
            colunas_finais = ["NumRps", "DtEmi", "VlNFS", "CpfCnpTom", "RazSocTom"]
            for c in colunas_finais:
                if c not in df.columns:
                    raise ValueError(f"Coluna alvo obrigatória não encontrada/identificada: {c}")
                    
            df_cleaned = df[colunas_finais].copy()
            
            # Retira linhas onde NumRps é vazio (provável totalizador ou lixo)
            df_cleaned.dropna(subset=["NumRps", "CpfCnpTom"], inplace=True)
            
            # Tratamento primário (limpar zeros e espaços)
            df_cleaned["NumRps"] = df_cleaned["NumRps"].astype(str).str.replace(".0", "", regex=False).str.strip()
            df_cleaned["CpfCnpTom"] = df_cleaned["CpfCnpTom"].astype(str).str.strip()
            
            return df_cleaned.to_dict(orient="records")
            
        except Exception as e:
            raise ValueError(f"Falha ao ler o arquivo ERP: {str(e)}")
