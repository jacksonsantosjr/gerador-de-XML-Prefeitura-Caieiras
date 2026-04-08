from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Gerador XML - Prefeitura de Caieiras"
    # Banco de Dados (Supabase)
    DATABASE_URL: str = "sqlite:///./caieiras.db" # Default temporário caso env falhe

    # Prefeitura (Valores fixos fornecidos pelo cliente)
    CODIGO_USUARIO: str = "e5fdfe91-6b2c-4f6b-8f4d-0159b5aff9d946sa52ri3064eiac000-ed17-o8i"
    CODIGO_CONTRIBUINTE: str = "df90f966-fa87-42b0-9de8-535c65a5946987sa10ri0046eiac032-ed56-o4i"
    PRESTADOR_CNPJ: str = "71896880000174"
    COD_SERVICO_FIXO: str = "17.02"
    DISCRIMINACAO_FIXA: str = "SERVICOS DE DATILOGRAFIA E DIGITACAO"
    PADRAO_COD_CTN: str = "170201000"
    PADRAO_COD_NBS: str = "118065900"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
