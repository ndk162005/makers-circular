from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..database import get_db

router = APIRouter(prefix="/api/stats", tags=["Stats"])

@router.get("", response_model=schemas.StatsResponse)
def get_stats(dataset_id: int, db: Session = Depends(get_db)):
    return crud.get_stats(db, dataset_id)
