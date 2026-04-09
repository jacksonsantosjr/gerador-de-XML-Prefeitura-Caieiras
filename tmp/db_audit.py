import os
import sys
from sqlalchemy import create_engine, text

# Hardcoded from .env for the check
DATABASE_URL = "postgresql://postgres:J%40ck%24oN%2140580%2A%23@db.lkgqqhkmrepphznlsewc.supabase.co:5432/postgres"

print(f"Connecting to: db.lkgqqhkmrepphznlsewc.supabase.co")

engine = create_engine(DATABASE_URL)
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT count(*) FROM tomadores"))
        count = result.scalar()
        print(f"--- TOTAL RECORDS IN 'tomadores': {count} ---")
        
        # Check first 5 to see data
        result = conn.execute(text("SELECT cnpj, razao_social FROM tomadores ORDER BY razao_social LIMIT 10"))
        print("--- FIRST 10 RECORDS (A-Z) ---")
        for row in result:
            print(f"- {row[0]}: {row[1]}")
            
        result = conn.execute(text("SELECT cnpj, razao_social FROM tomadores ORDER BY razao_social DESC LIMIT 10"))
        print("--- LAST 10 RECORDS (A-Z) ---")
        for row in result:
            print(f"- {row[0]}: {row[1]}")
            
except Exception as e:
    print(f"DB Error: {e}")
