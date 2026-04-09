import os
import sys

# Adiciona o diretório backend ao path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'backend')))

from app.core.database import SessionLocal
from app.models.tomador import Tomador

def check_count():
    db = SessionLocal()
    try:
        count = db.query(Tomador).count()
        print(f"Total de tomadores no banco: {count}")
    finally:
        db.close()

if __name__ == "__main__":
    check_count()
