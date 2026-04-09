import pandas as pd
import os
import uuid

# Configurações
import_filename = "TEMPLATE MODELO ENVIO DE RPS EM LOTE - PREF. CAIEIRAS.xlsm"
EXCEL_PATH = os.path.join(os.getcwd(), import_filename)
OUTPUT_SQL = "carga_tomadores.sql"

def clean_sql_value(val):
    if pd.isna(val) or str(val).lower() == 'nan':
        return "NULL"
    # Escapar aspas simples para SQL e remover espaços extras
    cleaned = str(val).replace("'", "''").strip()
    return f"'{cleaned}'"

def generate_sql():
    print(f"Lendo planilha: {EXCEL_PATH}")
    
    if not os.path.exists(EXCEL_PATH):
        print("Erro: Planilha nao encontrada na raiz do projeto.")
        return

    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name='Cadastro Atualizado')
        print(f"Sucesso: {len(df)} linhas encontradas.")

        sql_lines = [
            "-- Script de Carga Massiva de Tomadores (Jackson Junior)",
            "-- Gerado automaticamente para contornar bloqueios de rede local",
            "BEGIN;",
            ""
        ]

        for _, row in df.iterrows():
            cnpj_raw = str(row['CNPJ']).replace('.', '').replace('/', '').replace('-', '').strip()
            if not cnpj_raw or len(cnpj_raw) < 11:
                continue

            # Mapeamento de colunas baseado no modelo tomador.py
            params = {
                "cnpj": f"'{cnpj_raw}'",
                "razao_social": clean_sql_value(row['RAZÃO SOCIAL']),
                "tipo_logradouro": clean_sql_value(row['TIPO LOGRADOURO']),
                "logradouro": clean_sql_value(row['LOGRADOURO']),
                "numero": clean_sql_value(row['NÚMERO']),
                "cep": clean_sql_value(str(row['CEP']).replace('-', '').zfill(8) if pd.notna(row['CEP']) else ""),
                "bairro": clean_sql_value(row['BAIRRO']),
                "municipio": clean_sql_value(row['MUNICIPIO']),
                "uf": clean_sql_value(row['UF']),
                "complemento": "NULL" # Nao mapeado no excel original mas existe no banco
            }

            # Montagem do comando INSERT ... ON CONFLICT
            # Usando gen_random_uuid() do Postgres/Supabase
            insert_stmt = f"""INSERT INTO tomadores (id, cnpj, razao_social, tipo_logradouro, logradouro, numero, cep, bairro, municipio, uf, created_at, updated_at)
VALUES (gen_random_uuid(), {params['cnpj']}, {params['razao_social']}, {params['tipo_logradouro']}, {params['logradouro']}, {params['numero']}, {params['cep']}, {params['bairro']}, {params['municipio']}, {params['uf']}, now(), now())
ON CONFLICT (cnpj) DO UPDATE SET
    razao_social = EXCLUDED.razao_social,
    logradouro = EXCLUDED.logradouro,
    updated_at = now();"""
            
            sql_lines.append(insert_stmt)

        sql_lines.append("")
        sql_lines.append("COMMIT;")

        with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
            f.write("\n".join(sql_lines))

        print(f"\n--- SUCESSO ---")
        print(f"Arquivo gerado: {OUTPUT_SQL}")
        print(f"Total de comandos: {len(sql_lines) - 5}")
        print(f"Instrucao: Abra este arquivo, copie tudo e cole no SQL Editor do Supabase.")

    except Exception as e:
        print(f"Erro ao processar Excel: {str(e)}")

if __name__ == "__main__":
    generate_sql()
