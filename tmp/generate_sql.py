import pandas as pd
import uuid

EXCEL_PATH = r"C:\Users\jackson.junior\Downloads\TEMPLATE MODELO ENVIO DE RPS EM LOTE - PREF. CAIEIRAS.xlsm"

def generate_sql():
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name='Cadastro Atualizado')
        
        sql_lines = []
        sql_lines.append("-- SQL Script para Importação Manual no Supabase")
        sql_lines.append("INSERT INTO tomadores (id, cnpj, razao_social, tipo_logradouro, logradouro, numero, cep, bairro, municipio, uf, created_at, updated_at)")
        sql_lines.append("VALUES")

        values = []
        for index, row in df.iterrows():
            cnpj_clean = str(row['CNPJ']).replace('.', '').replace('/', '').replace('-', '').strip()
            razao = str(row['RAZÃO SOCIAL']).replace("'", "''").strip()
            tipo = str(row['TIPO LOGRADOURO']).strip() if pd.notna(row['TIPO LOGRADOURO']) else "RUA"
            logr = str(row['LOGRADOURO']).replace("'", "''").strip() if pd.notna(row['LOGRADOURO']) else ""
            num = str(row['NÚMERO']).replace("'", "''").strip() if pd.notna(row['NÚMERO']) else "S/N"
            cep = str(row['CEP']).zfill(8) if pd.notna(row['CEP']) else ""
            bairro = str(row['BAIRRO']).replace("'", "''").strip() if pd.notna(row['BAIRRO']) else ""
            city = str(row['MUNICIPIO']).replace("'", "''").strip() if pd.notna(row['MUNICIPIO']) else ""
            uf = str(row['UF']).strip() if pd.notna(row['UF']) else ""
            
            val = f"('{uuid.uuid4()}', '{cnpj_clean}', '{razao}', '{tipo}', '{logr}', '{num}', '{cep}', '{bairro}', '{city}', '{uf}', now(), now())"
            values.append(val)

        sql_lines.append(",\n".join(values))
        sql_lines.append("ON CONFLICT (cnpj) DO UPDATE SET")
        sql_lines.append("  razao_social = EXCLUDED.razao_social,")
        sql_lines.append("  logradouro = EXCLUDED.logradouro,")
        sql_lines.append("  bairro = EXCLUDED.bairro,")
        sql_lines.append("  updated_at = now();")

        with open('tmp/importar_tomadores.sql', 'w', encoding='utf-8') as f:
            f.write("\n".join(sql_lines))
        
        print("SQL gerado em tmp/importar_tomadores.sql")
        print(f"Total de registros: {len(values)}")
        
    except Exception as e:
        print(f"Erro: {str(e)}")

if __name__ == "__main__":
    generate_sql()
