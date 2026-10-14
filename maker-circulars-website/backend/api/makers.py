from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud
from ..database import get_db

router = APIRouter(prefix="/api/makers", tags=["Makers"])

@router.get("", response_model=List[schemas.MakerResponse])
def get_makers(dataset_id: int, db: Session = Depends(get_db)):
    return crud.get_makers(db, dataset_id)
