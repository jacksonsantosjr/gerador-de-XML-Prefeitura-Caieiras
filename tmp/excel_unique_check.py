import pandas as pd
import os

EXCEL_PATH = r"C:\Users\jackson.junior\Downloads\TEMPLATE MODELO ENVIO DE RPS EM LOTE - PREF. CAIEIRAS.xlsm"

if os.path.exists(EXCEL_PATH):
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name='Cadastro Atualizado')
        unique_cnpjs = df['CNPJ'].dropna().unique()
        print(f"--- TOTAL ROWS: {len(df)} ---")
        print(f"--- UNIQUE CNPJs: {len(unique_cnpjs)} ---")
        
        # Check first few unique ones
        print("--- SAMPLE UNIQUE RAZÕES (First 10) ---")
        unique_names = df['RAZÃO SOCIAL'].dropna().unique()
        for name in unique_names[:10]:
            print(f"- {name}")
            
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Excel not found.")
