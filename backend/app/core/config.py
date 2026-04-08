from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Gerador XML - Prefeitura de Caieiras"
    # Banco de Dados (Supabase)
    DATABASE_URL: str = "sqlite:///./caieiras.db" # Default temporário caso env falhe

    # Prefeitura
    CODIGO_USUARIO: str = ""
    CODIGO_CONTRIBUINTE: str = ""
    PRESTADOR_CNPJ: str = ""
    COD_SERVICO_FIXO: str = "17.02"
    DISCRIMINACAO_FIXA: str = "SERVICOS DE DATILOGRAFIA E DIGITACAO"
    PADRAO_COD_CTN: str = "170201000"
    PADRAO_COD_NBS: str = "118065900"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
