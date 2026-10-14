import os
import time
from sqlalchemy.orm import Session
from .. import models
from ..crud import get_stats

def check_duplicate_dataset(filename: str, row_count: int, column_names: list, db: Session):
    """Check if a similar dataset already exists based on filename and row count."""
    similar = db.query(models.Dataset).filter(
        models.Dataset.filename == filename,
        models.Dataset.row_count == row_count
    ).first()
    return similar is not None

def find_similar_dataset(filename: str, row_count: int, db: Session):
    """Find a similar dataset by filename and row count."""
    return db.query(models.Dataset).filter(
        models.Dataset.filename == filename,
        models.Dataset.row_count == row_count
    ).first()

def get_dataset_stats(dataset_id: int, db: Session):
    """Get statistics for a dataset."""
    return get_stats(db, dataset_id)

def cleanup_uploads(uploads_dir: str, max_age_seconds: int = 86400):
    """Remove uploaded files older than max_age_seconds."""
    now = time.time()
    for filename in os.listdir(uploads_dir):
        if filename == ".gitkeep":
            continue
        filepath = os.path.join(uploads_dir, filename)
        if os.path.isfile(filepath):
            if os.stat(filepath).st_mtime < now - max_age_seconds:
                try:
                    os.remove(filepath)
                except Exception:
                    pass
