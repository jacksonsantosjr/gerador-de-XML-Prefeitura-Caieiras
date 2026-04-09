import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"Connecting to: {DATABASE_URL.split('@')[-1]}") # Log host only for safety

engine = create_engine(DATABASE_URL)
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT count(*) FROM tomadores"))
        count = result.scalar()
        print(f"--- TOTAL RECORDS IN 'tomadores': {count} ---")
        
        # Check first 5 to see data
        result = conn.execute(text("SELECT cnpj, razao_social FROM tomadores LIMIT 5"))
        print("--- FIRST 5 RECORDS ---")
        for row in result:
            print(row)
except Exception as e:
    print(f"DB Error: {e}")
