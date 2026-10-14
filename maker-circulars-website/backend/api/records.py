from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..database import get_db

router = APIRouter(prefix="/api/records", tags=["Records"])

@router.get("", response_model=schemas.PaginatedResponse)
def read_records(
    dataset_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    search: str = None,
    maker: str = None,
    sort_by: str = None,
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    only_new: bool = Query(False),
    db: Session = Depends(get_db)
):
    records, total = crud.get_records(db, dataset_id, page, page_size, search, maker, sort_by, sort_order, only_new=only_new)
    return {
        "items": records,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/{record_id}", response_model=schemas.RecordResponse)
def read_record(record_id: int, db: Session = Depends(get_db)):
    record = crud.get_record(db, record_id=record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@router.post("", response_model=schemas.RecordResponse)
def create_record(record: schemas.RecordCreate, db: Session = Depends(get_db)):
    from ..models import Record
    db_record = Record(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.put("/{record_id}", response_model=schemas.RecordResponse)
def update_record(record_id: int, record: schemas.RecordUpdate, db: Session = Depends(get_db)):
    db_record = crud.update_record(db, record_id=record_id, data=record.data)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return db_record

@router.delete("/{record_id}", response_model=schemas.RecordResponse)
def delete_record(record_id: int, db: Session = Depends(get_db)):
    db_record = crud.delete_record(db, record_id=record_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return db_record
