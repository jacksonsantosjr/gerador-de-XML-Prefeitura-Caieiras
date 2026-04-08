import pandas as pd
import sys

file_path = r"C:\Users\jackson.junior\Downloads\TEMPLATE MODELO ENVIO DE RPS EM LOTE - PREF. CAIEIRAS.xlsm"

try:
    df = pd.read_excel(file_path, sheet_name='Cadastro Atualizado')
    print("COLUMNS:")
    print(df.columns.tolist())
    print("\nSAMPLE:")
    print(df.head(5).to_json(orient='records'))
except Exception as e:
    print(f"ERROR: {str(e)}")
