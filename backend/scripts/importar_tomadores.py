import pandas as pd
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Adiciona o diretório app ao path para importar as configurações se necessário
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

EXCEL_PATH = r"C:\Users\jackson.junior\Downloads\TEMPLATE MODELO ENVIO DE RPS EM LOTE - PREF. CAIEIRAS.xlsm"

def import_tomadores():
    print(f"Iniciando importacao de: {EXCEL_PATH}")
    
    if not os.path.exists(EXCEL_PATH):
        print(f"Erro: Arquivo nao encontrado em {EXCEL_PATH}")
        return

    try:
        # Lendo apenas a aba desejada
        df = pd.read_excel(EXCEL_PATH, sheet_name='Cadastro Atualizado')
        print(f"Foram encontradas {len(df)} linhas no Excel.")

        # Mapeamento de colunas (Excel -> Banco)
        # Excel: ['CNPJ', 'RAZÃO SOCIAL', 'TIPO LOGRADOURO', 'LOGRADOURO', 'NÚMERO', 'CEP', 'BAIRRO', 'MUNICIPIO', 'UF']
        
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        count_new = 0
        count_updated = 0

        for index, row in df.iterrows():
            cnpj_clean = str(row['CNPJ']).replace('.', '').replace('/', '').replace('-', '').strip()
            
            # Upsert manual (ou merge)
            # Verifica se já existe
            query = text("SELECT id FROM tomadores WHERE cnpj = :cnpj")
            result = session.execute(query, {"cnpj": cnpj_clean}).fetchone()

            params = {
                "cnpj": cnpj_clean,
                "razao_social": str(row['RAZÃO SOCIAL']).strip(),
                "tipo_logradouro": str(row['TIPO LOGRADOURO']).strip() if pd.notna(row['TIPO LOGRADOURO']) else "RUA",
                "logradouro": str(row['LOGRADOURO']).strip() if pd.notna(row['LOGRADOURO']) else "",
                "numero": str(row['NÚMERO']).strip() if pd.notna(row['NÚMERO']) else "S/N",
                "cep": str(row['CEP']).zfill(8) if pd.notna(row['CEP']) else "",
                "bairro": str(row['BAIRRO']).strip() if pd.notna(row['BAIRRO']) else "",
                "municipio": str(row['MUNICIPIO']).strip() if pd.notna(row['MUNICIPIO']) else "",
                "uf": str(row['UF']).strip() if pd.notna(row['UF']) else ""
            }

            if result:
                # Update
                update_query = text("""
                    UPDATE tomadores 
                    SET razao_social = :razao_social, tipo_logradouro = :tipo_logradouro, 
                        logradouro = :logradouro, numero = :numero, cep = :cep, 
                        bairro = :bairro, municipio = :municipio, uf = :uf, updated_at = now()
                    WHERE cnpj = :cnpj
                """)
                session.execute(update_query, params)
                count_updated += 1
            else:
                # Insert
                insert_query = text("""
                    INSERT INTO tomadores (id, cnpj, razao_social, tipo_logradouro, logradouro, numero, cep, bairro, municipio, uf, created_at, updated_at)
                    VALUES (gen_random_uuid(), :cnpj, :razao_social, :tipo_logradouro, :logradouro, :numero, :cep, :bairro, :municipio, :uf, now(), now())
                """)
                session.execute(insert_query, params)
                count_new += 1

        session.commit()
        session.close()

        print(f"Importacao finalizada com sucesso!")
        print(f"   - Novos clientes: {count_new}")
        print(f"   - Clientes atualizados: {count_updated}")

    except Exception as e:
        print(f"Erro critico: {str(e)}")

if __name__ == "__main__":
    import_tomadores()
