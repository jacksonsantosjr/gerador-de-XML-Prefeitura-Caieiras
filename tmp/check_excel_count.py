import pandas as pd
import os

EXCEL_PATH = r"C:\Users\jackson.junior\Downloads\TEMPLATE MODELO ENVIO DE RPS EM LOTE - PREF. CAIEIRAS.xlsm"

if os.path.exists(EXCEL_PATH):
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name='Cadastro Atualizado')
        print(f"--- ROWS IN EXCEL 'Cadastro Atualizado': {len(df)} ---")
    except Exception as e:
        print(f"Error reading excel: {e}")
else:
    print("Excel file not found at path.")
