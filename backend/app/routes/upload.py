from fastapi import APIRouter, File, UploadFile, Depends, Form, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.services.spreadsheet_parser import SpreadsheetParser
from app.services.value_calculator import ValueCalculator
from app.services.data_enrichment import EnrichmentService
from app.services.xml_generator import XmlGeneratorService

router = APIRouter()

@router.post("/processar")
async def process_file(
    file: UploadFile = File(...),
    competencia: str = Form(...),  # Mês/Ano: ex 2026-03
    db: Session = Depends(get_db)
):
    """
    Recebe a planilha Excel.
    1. Parseia os dados CSV/XLSX
    2. Cruza com Supabase/BrasilAPI para endereços
    3. Calcula o ISS/NFS
    4. Gera o XML Lote.
    """
    
    # 1. Validação de formato (case-insensitive)
    if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="Formato não suportado. Envie CSV ou Excel.")

    contents = await file.read()
    
    # 2. Extract Data (Spreadsheet parser)
    try:
        raw_rows = SpreadsheetParser.parse_file(contents, file.filename)
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro fatal lendo o arquivo: {str(e)}")

    if not raw_rows:
        raise HTTPException(status_code=400, detail="Nenhum dado legível encontrado no arquivo.")

    # 3. Aplicar Cálculo de Imposto Rápido 
    rows_calculated = []
    for row in raw_rows:
        rows_calculated.append(ValueCalculator.process_taxes(row))

    # 4. Enriquecer (Supabase + BrasilAPI)
    try:
        enriched_rows, stats = await EnrichmentService.enrich_and_verify_tomadores(db, rows_calculated)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro conectando ao Supabase ou BrasilAPI: {str(e)}")

    # 5. Avaliação do Frontend (Se houver faltando o cep na BrasilAPI ele marca como MISSING_ADDRESS)
    # Mas num fluxo fluído o XML pode ignorar os erros, gerando com S/N e "Nao Informado".
    
    # 6. Gerar XML LXML
    try:
        xml_bytes, warnings = XmlGeneratorService.gerar_lote_xml(enriched_rows, data_competencia=competencia)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro gerando estrutura XML: {str(e)}")

    import base64
    xml_b64 = base64.b64encode(xml_bytes).decode('utf-8')

    return {
        "status": "success",
        "stats": {
            "total_notas": stats["total_notas"],
            "novos_clientes": stats["tomadores_novos_brasilapi"]
        },
        "warnings": warnings,
        "rows": enriched_rows,  # Retorna os dados para edição no frontend
        "xml_base64": xml_b64,
        "filename": f"RPS_CAIEIRAS_{competencia}.xml"
    }

@router.post("/reprocessar")
async def reprocess_data(
    payload: dict,
    db: Session = Depends(get_db)
):
    """
    Recebe os dados editados do frontend e gera um novo XML na hora.
    """
    rows = payload.get("rows")
    competencia = payload.get("competencia")

    if not rows:
        raise HTTPException(status_code=400, detail="Dados de 'rows' não fornecidos.")

    # 1. Recalcular impostos caso o usuário tenha mudado valores (segurança)
    # No momento as edições são focadas em tomadores, mas o calculator garante integridade.
    rows_calculated = []
    for row in rows:
        rows_calculated.append(ValueCalculator.process_taxes(row))

    # 2. Gerar XML LXML
    try:
        xml_bytes, warnings = XmlGeneratorService.gerar_lote_xml(rows_calculated, data_competencia=competencia)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro regerando estrutura XML: {str(e)}")

    import base64
    xml_b64 = base64.b64encode(xml_bytes).decode('utf-8')

    return {
        "status": "success",
        "warnings": warnings,
        "rows": rows_calculated,
        "xml_base64": xml_b64,
        "filename": f"RPS_CAIEIRAS_{competencia}_CORRIGIDO.xml"
    }
