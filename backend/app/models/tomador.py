from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class Tomador(Base):
    __tablename__ = "tomadores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cnpj = Column(String(20), unique=True, nullable=False, index=True)
    razao_social = Column(String(255), nullable=False)
    tipo_logradouro = Column(String(50), default="RUA")
    logradouro = Column(String(255))
    numero = Column(String(50), default="S/N")
    complemento = Column(String(100))
    bairro = Column(String(150))
    municipio = Column(String(150))
    uf = Column(String(2))
    cep = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
