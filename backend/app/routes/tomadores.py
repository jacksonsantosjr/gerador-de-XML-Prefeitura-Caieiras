from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.tomador import Tomador
from typing import List

router = APIRouter()

@router.get("/tomadores")
def list_tomadores(db: Session = Depends(get_db)):
    """Lista todos os tomadores salvos no banco de dados Supabase."""
    tomadores = db.query(Tomador).order_by(Tomador.razao_social).all()
    return tomadores
