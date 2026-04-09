import os
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# Tentativa de hosts diferentes do Supabase para o projeto lkgqqhkmrepphznlsewc
hosts = [
    "db.lkgqqhkmrepphznlsewc.supabase.co",
    "aws-0-us-east-1.pooler.supabase.com"
]

password_raw = "J@ck$oN!40580*#" 
password = quote_plus(password_raw)
user = "postgres"
dbname = "postgres"

EXCEL_PATH = r"C:\Users\jackson.junior\Downloads\TEMPLATE MODELO ENVIO DE RPS EM LOTE - PREF. CAIEIRAS.xlsm"

def try_import():
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name='Cadastro Atualizado')
        print(f"Excel rows found: {len(df)}")
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return

    for host in hosts:
        for p in ["5432", "6543"]:
            # URL construída com password já escapado
            url = f"postgresql://{user}:{password}@{host}:{p}/{dbname}"
            print(f"Trying to connect to {host}:{p}...")
            try:
                engine = create_engine(url, connect_args={'connect_timeout': 5})
                with engine.connect() as conn:
                    print(f"Success! Connected to {host}:{p}")
                    
                    # Usar transação para garantir atomicidade
                    with conn.begin():
                        print("Truncating table...")
                        conn.execute(text("TRUNCATE TABLE tomadores"))
                        
                        count = 0
                        for _, row in df.iterrows():
                            cnpj_clean = str(row['CNPJ']).replace('.', '').replace('/', '').replace('-', '').strip()
                            # Se o CNPJ for vazio ou inválido, pula
                            if not cnpj_clean or len(cnpj_clean) < 11:
                                continue
                                
                            params = {
                                "cnpj": cnpj_clean,
                                "razao_social": str(row['RAZÃO SOCIAL']).strip(),
                                "tipo_logradouro": str(row['TIPO LOGRADOURO']).strip() if pd.notna(row['TIPO LOGRADOURO']) else "RUA",
                                "logradouro": str(row['LOGRADOURO']).strip() if pd.notna(row['LOGRADOURO']) else "",
                                "numero": str(row['NÚMERO']).strip() if pd.notna(row['NÚMERO']) else "S/N",
                                "cep": str(row['CEP']).replace('-', '').zfill(8) if pd.notna(row['CEP']) else "",
                                "bairro": str(row['BAIRRO']).strip() if pd.notna(row['BAIRRO']) else "",
                                "municipio": str(row['MUNICIPIO']).strip() if pd.notna(row['MUNICIPIO']) else "",
                                "uf": str(row['UF']).strip() if pd.notna(row['UF']) else ""
                            }
                            
                            insert_query = text("""
                                INSERT INTO tomadores (id, cnpj, razao_social, tipo_logradouro, logradouro, numero, cep, bairro, municipio, uf, created_at, updated_at)
                                VALUES (gen_random_uuid(), :cnpj, :razao_social, :tipo_logradouro, :logradouro, :numero, :cep, :bairro, :municipio, :uf, now(), now())
                                ON CONFLICT (cnpj) DO NOTHING
                            """)
                            conn.execute(insert_query, params)
                            count += 1
                        
                        print(f"Processed {count} records successfully.")
                    return 
            except Exception as e:
                print(f"Connection failed for {host}:{p}")
                # print(f"Error: {e}") # Evitar vazar senha se houver erro bruto

if __name__ == "__main__":
    try_import()
