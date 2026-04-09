import os
from sqlalchemy import create_engine, text

# Hardcoded for check if env fails, but let's try to get it
DATABASE_URL = "postgresql://postgres.itoywobvjueyospxqghj:jackson102030@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text("SELECT count(*) FROM clientes"))
    count = result.scalar()
    print(f"--- TOTAL RECORDS IN 'clientes': {count} ---")
    
    # Check if there are some without razao_social
    result = conn.execute(text("SELECT count(*) FROM clientes WHERE razao_social IS NULL OR razao_social = ''"))
    empty = result.scalar()
    print(f"--- RECORDS WITHOUT RAZAO SOCIAL: {empty} ---")
