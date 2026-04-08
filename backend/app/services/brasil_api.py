import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class BrasilAPIService:
    BASE_URL = "https://brasilapi.com.br/api/cnpj/v1"

    @classmethod
    async def fetch_cnpj_data(cls, cnpj: str) -> Optional[Dict[str, Any]]:
        """Busca os dados de um CNPJ na BrasilAPI."""
        clean_cnpj = ''.join(filter(str.isdigit, str(cnpj)))
        
        # Só buscamos na BrasilAPI se for CNPJ (14 dígitos). CPF não é suportado lá.
        if len(clean_cnpj) != 14:
            return None
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{cls.BASE_URL}/{clean_cnpj}", timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "cnpj": clean_cnpj,
                        "razao_social": data.get("razao_social", ""),
                        "tipo_logradouro": data.get("descricao_tipo_de_logradouro", "RUA"),
                        "logradouro": data.get("logradouro", ""),
                        "numero": data.get("numero", "S/N"),
                        "complemento": data.get("complemento", ""),
                        "bairro": data.get("bairro", ""),
                        "municipio": data.get("municipio", ""),
                        "uf": data.get("uf", ""),
                        "cep": str(data.get("cep", "")).replace(".", "").replace("-", "")
                    }
                return None
            except httpx.RequestError as e:
                logger.error(f"Erro ao buscar CNPJ {clean_cnpj} na BrasilAPI: {e}")
                return None
