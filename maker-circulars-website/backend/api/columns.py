from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud
from ..database import get_db

router = APIRouter(prefix="/api/columns", tags=["Columns"])

@router.get("", response_model=List[schemas.ColumnResponse])
def get_columns(dataset_id: int, db: Session = Depends(get_db)):
    return crud.get_columns(db, dataset_id)

@router.post("", response_model=schemas.ColumnResponse)
def add_column(column: schemas.ColumnCreate, db: Session = Depends(get_db)):
    return crud.add_column(db, column)

@router.put("/{column_id}", response_model=schemas.ColumnResponse)
def rename_column(column_id: int, column: schemas.ColumnUpdate, db: Session = Depends(get_db)):
    db_col = crud.rename_column(db, column_id, column)
    if not db_col:
        raise HTTPException(status_code=404, detail="Column not found")
    return db_col

@router.delete("/{column_id}", response_model=schemas.ColumnResponse)
def delete_column(column_id: int, db: Session = Depends(get_db)):
    db_col = crud.delete_column(db, column_id)
    if not db_col:
        raise HTTPException(status_code=404, detail="Column not found")
    return db_col
