from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.tomador import Tomador
from app.schemas.tomador import TomadorUpdate
from typing import List

router = APIRouter()

@router.get("/tomadores")
def list_tomadores(db: Session = Depends(get_db)):
    """Lista todos os tomadores salvos no banco de dados Supabase."""
    tomadores = db.query(Tomador).order_by(Tomador.razao_social).all()
    return tomadores

@router.patch("/tomadores/{cnpj}")
def update_tomador(cnpj: str, obj_in: TomadorUpdate, db: Session = Depends(get_db)):
    """Atualiza dados de um tomador pelo CNPJ (Upsert se necessário, mas aqui focado em correção)."""
    tomador = db.query(Tomador).filter(Tomador.cnpj == cnpj).first()
    if not tomador:
        # Se não existir, podemos criar ou retornar erro. 
        # No fluxo de correção, o tomador deveria existir (foi enrich ou importado).
        # Para garantir, vamos fazer um Upsert se for necessário no futuro, 
        # mas por hora, vamos apenas atualizar.
        return {"error": "Tomador não encontrado para atualização."}
    
    update_data = obj_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(tomador, field, update_data[field])
    
    db.commit()
    db.refresh(tomador)
    return tomador
