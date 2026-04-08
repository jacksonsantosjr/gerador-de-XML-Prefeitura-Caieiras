from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
import uuid

class TomadorBase(BaseModel):
    cnpj: str = Field(..., max_length=20, description="CNPJ do Tomador")
    razao_social: str = Field(..., max_length=255, description="Razão Social/Nome")
    tipo_logradouro: Optional[str] = Field("RUA", max_length=50)
    logradouro: Optional[str] = Field(None, max_length=255)
    numero: Optional[str] = Field("S/N", max_length=50)
    complemento: Optional[str] = Field(None, max_length=100)
    bairro: Optional[str] = Field(None, max_length=150)
    municipio: Optional[str] = Field(None, max_length=150)
    uf: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, max_length=20)

class TomadorCreate(TomadorBase):
    pass

class TomadorUpdate(BaseModel):
    razao_social: Optional[str] = None
    tipo_logradouro: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None
    cep: Optional[str] = None

class TomadorResponse(TomadorBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
