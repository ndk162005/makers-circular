from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..database import get_db

router = APIRouter(prefix="/api/datasets", tags=["Datasets"])

@router.get("", response_model=schemas.DatasetListResponse)
def read_datasets(db: Session = Depends(get_db)):
    datasets, total = crud.get_datasets(db)
    return {"items": datasets, "total": total}

@router.get("/{dataset_id}", response_model=schemas.DatasetResponse)
def read_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = crud.get_dataset(db, dataset_id=dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@router.delete("/{dataset_id}", response_model=schemas.DatasetResponse)
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = crud.delete_dataset(db, dataset_id=dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset
