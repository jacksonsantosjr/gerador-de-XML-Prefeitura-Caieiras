from fastapi import APIRouter, Depends, HTTPException
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
    """Atualiza dados de um tomador pelo CNPJ."""
    tomador = db.query(Tomador).filter(Tomador.cnpj == cnpj).first()
    update_data = obj_in.model_dump(exclude_unset=True)
    
    if not tomador:
        # Cria um novo tomador (Upsert)
        if 'razao_social' not in update_data or not update_data['razao_social']:
            update_data['razao_social'] = "RAZÃO SOCIAL NÃO INFORMADA"
            
        tomador = Tomador(cnpj=cnpj, **update_data)
        db.add(tomador)
    else:
        for field in update_data:
            setattr(tomador, field, update_data[field])
    
    db.commit()
    db.refresh(tomador)
    return tomador
