from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ColumnBase(BaseModel):
    name: str
    data_type: str = "text"
    position: Optional[int] = 0
    is_active: Optional[bool] = True

class ColumnCreate(ColumnBase):
    dataset_id: int

class ColumnUpdate(BaseModel):
    name: Optional[str] = None
    data_type: Optional[str] = None
    position: Optional[int] = None
    is_active: Optional[bool] = None

class ColumnResponse(ColumnBase):
    id: int
    dataset_id: int
    class Config:
        from_attributes = True

class DatasetBase(BaseModel):
    filename: str
    worksheet_name: Optional[str] = None

class DatasetResponse(DatasetBase):
    id: int
    uploaded_at: Optional[datetime] = None
    row_count: Optional[int] = 0
    column_count: Optional[int] = 0
    column_names: Optional[List[str]] = []
    status: Optional[str] = "active"
    class Config:
        from_attributes = True

class DatasetListResponse(BaseModel):
    items: List[DatasetResponse]
    total: int

class RecordBase(BaseModel):
    data: Dict[str, Any]

class RecordCreate(RecordBase):
    dataset_id: int

class RecordUpdate(RecordBase):
    pass

class RecordResponse(RecordBase):
    id: int
    dataset_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel):
    items: List[RecordResponse]
    total: int
    page: int
    page_size: int

class DuplicateWarning(BaseModel):
    existing_dataset_id: int
    existing_filename: str

class ImportPreviewResponse(BaseModel):
    file_id: str
    filename: str
    sheet_names: List[str]
    columns: List[str]
    row_count: int
    preview_data: List[Dict[str, Any]]
    duplicate_warning: Optional[DuplicateWarning] = None

class ImportConfirmRequest(BaseModel):
    file_id: str
    sheet_name: str
    import_mode: str = "new"
    existing_dataset_id: Optional[int] = None

class MakerResponse(BaseModel):
    maker: Optional[str] = None
    count: int

class StatsResponse(BaseModel):
    total_records: int
    total_makers: int
    docs_with_links: int
    records_with_dms: Optional[int] = 0
    newly_added_records: int = 0
