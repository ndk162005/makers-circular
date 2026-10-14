import os
import uuid
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from .. import schemas
from ..database import get_db, UPLOADS_DIR
from ..services import excel_importer, database_service
from ..crud import create_dataset

router = APIRouter(prefix="/api/import", tags=["Import"])

# Store mapping of file_id to original filename in memory
_file_metadata = {}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = excel_importer.validate_file(file)
    
    # Read file content to check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB.")
    
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(filename)[1]
    safe_filename = f"{file_id}{ext}"
    file_path = os.path.join(UPLOADS_DIR, safe_filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # Store original filename mapping
    _file_metadata[safe_filename] = filename
    
    sheet_names = excel_importer.parse_excel(file_path)
    return {"file_id": safe_filename, "sheet_names": sheet_names, "original_filename": filename}


class PreviewRequest(BaseModel):
    file_id: str
    sheet_name: Optional[str] = None


@router.post("/preview")
def preview_import(req: PreviewRequest, db: Session = Depends(get_db)):
    file_path = os.path.join(UPLOADS_DIR, req.file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found. Please upload again.")
    
    # Prevent path traversal
    real_path = os.path.realpath(file_path)
    real_uploads = os.path.realpath(UPLOADS_DIR)
    if not real_path.startswith(real_uploads):
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    preview = excel_importer.generate_preview(file_path, req.sheet_name)
    original_filename = _file_metadata.get(req.file_id, req.file_id)
    
    # Check for duplicate
    duplicate_warning = None
    is_duplicate = database_service.check_duplicate_dataset(
        filename=original_filename,
        row_count=preview["row_count"],
        column_names=preview["columns"],
        db=db
    )
    if is_duplicate:
        similar = database_service.find_similar_dataset(
            filename=original_filename,
            row_count=preview["row_count"],
            db=db
        )
        if similar:
            duplicate_warning = {
                "existing_dataset_id": similar.id,
                "existing_filename": similar.filename
            }
    
    return {
        "file_id": req.file_id,
        "filename": original_filename,
        "sheet_names": preview["sheet_names"],
        "columns": preview["columns"],
        "row_count": preview["row_count"],
        "preview_data": preview["preview_data"],
        "duplicate_warning": duplicate_warning
    }


@router.post("/confirm")
def confirm_import(req: schemas.ImportConfirmRequest, db: Session = Depends(get_db)):
    file_path = os.path.join(UPLOADS_DIR, req.file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found. Please upload again.")
    
    # Prevent path traversal
    real_path = os.path.realpath(file_path)
    real_uploads = os.path.realpath(UPLOADS_DIR)
    if not real_path.startswith(real_uploads):
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    original_filename = _file_metadata.get(req.file_id, req.file_id)
    
    # Handle replace mode
    if req.import_mode == "replace" and hasattr(req, 'existing_dataset_id') and req.existing_dataset_id:
        from ..crud import delete_dataset
        delete_dataset(db, req.existing_dataset_id)
    
    dataset_schema = schemas.DatasetBase(
        filename=original_filename,
        worksheet_name=req.sheet_name
    )
    dataset = create_dataset(db, dataset_schema)
    
    excel_importer.import_data(file_path, req.sheet_name, dataset.id, db)
    
    # Cleanup the temporary file
    try:
        os.remove(file_path)
        _file_metadata.pop(req.file_id, None)
    except Exception:
        pass
    
    return {"dataset_id": dataset.id, "status": "success", "message": f"Successfully imported {dataset.row_count} records"}
