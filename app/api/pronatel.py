from http.client import HTTPException
from fastapi import APIRouter, UploadFile, File
from fastapi.response import FileResponse
from typing import Optional
from pydantic import BaseModel
import os
from datetime import datetime
import shutil

from app.modules.word_bots.pronatel.scripts.pronatel import fill_word_template

router = APIRouter(prefix="/api/reportes", tags=["reportes_tickets"])

class ProcessExcelResponse(BaseModel):
    message : str
    excel_id: str
    filename : str

class GenerateWordRequest(BaseModel):
    excel_id: str
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None

class Config:
    json_schema_extra = {
        "example":{
            "message": "Archivo excel procesado correctamente",
            "excel_id": "excel_20240131_123456",
            "file_name": "data.xlsx"
        }
    }

UPLOAD_DIR ="media/pronatel/data"
WORD_OUTPUT_DIR="media/prontel/output"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(WORD_OUTPUT_DIR, exist_ok=True)

@router.post("/upload-excel", response_model=ProcessExcelResponse)
async def upload_excel_file(file: UploadFile = File(...)):
    """
    Endpoint para subir el archivo excel con los datos de los tickets.

    Args:
    file: Archivo excel a subir

    Returns:
        ProcessExcelResponse: Informacion sobre el archivo procesado

    """

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_id = f"excel_{timestamp}"

        file_extension= os.path.splitext(file.filename)[1]
        filename = f"{excel_id}{file_extension}"
        file_path = os .path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return ProcessExcelResponse(
            message="Archivo excel procesado correctamente",
            excel_id=excel_id,
            filename=filename 
        )
    
    except Exception as e:
        raise HTTPException(
        status_code=500,
        detail=f"Error al procesar el archivo: {str(e)}"
        )
    

@router.post("/generate-word")
async def generate_word_report(request: GenerateWordRequest):
    """
    Endpoint para generar el reporte word basado en el Excel subido.

    Args:

    request: Datos para la generacion del reporte

    Returns:
        FileResponse: Archivo Word generado
    
    """

    try:
        excel_path = os.path.join(UPLOAD_DIR, f"{request.excel_id}.xlsx")
        word_template_path = "templates/reporte_template.docx"
        word_output_path = os.path.join(
            WORD_OUTPUT_DIR,
            f"reporte_{request.excel_id}.docx"
        )

        if not os.path.exists(excel_path):
            raise HTTPException(
                status_code=404,
                detail="Archivo excel no encontrado"
            )
        
        fill_word_template(
            excel_path=excel_path,
            word_template_path=word_template_path,
            word_output_path=word_output_path,
            fecha_inicio=request.fecha_inicio,
            fecha_fin=request.fecha_fin
        )

        if not os.path.exists(word_output_path):
            raise HTTPException(status_code=500, detail="Error: No se guardo el archivo Word.")

        return FileResponse(
            word_output_path,
            filename=f"reporte_tickets.docx",
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar el reporte: {str(e)}"
        )
    

        
    

    


        




    




