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
    
    # 1. Validação de formato
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
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
        xml_bytes = XmlGeneratorService.gerar_lote_xml(enriched_rows, data_competencia=competencia)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro gerando estrutura XML: {str(e)}")

    # 7. Disparar resposta em anexo para Download Automático
    headers = {
        'Content-Disposition': f'attachment; filename="RPS_CAIEIRAS_{competencia}.xml"',
        'X-Total-Notas': str(stats["total_notas"]),
        'X-Novos-Clientes': str(stats["tomadores_novos_brasilapi"])
    }
    
    return Response(content=xml_bytes, media_type="application/xml", headers=headers)
