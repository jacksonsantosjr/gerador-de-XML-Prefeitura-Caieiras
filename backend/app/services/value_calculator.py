from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any

class ValueCalculator:
    @staticmethod
    def extract_decimal(value: Any) -> Decimal:
        """Extrai um valor Decimal de forma segura a partir de string ou float."""
        if not value:
            return Decimal("0.00")
        try:
            # Substitui virgulas p/ formato de string americano se vier br
            str_val = str(value).replace(',', '.')
            return Decimal(str_val).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except:
            return Decimal("0.00")

    @classmethod
    def process_taxes(cls, row: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica a regra de negócio tributária em cima da linha."""
        v_nfs = cls.extract_decimal(row.get("VlNFS", "0"))
        
        # O VBA original calculava 2% se vazia. Vamos forçar a regra de 2% para Caieiras.
        v_iss = (v_nfs * Decimal("0.02")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        row["VlNFS_Calculado"] = v_nfs
        row["VlIss_Calculado"] = v_iss
        
        # Base de cálculo geralmente é igual ao VlNFS
        row["BaseCalc"] = v_nfs
        
        # Alíquota Fixa (2%)
        row["Aliquota"] = Decimal("0.02")
        
        return row
