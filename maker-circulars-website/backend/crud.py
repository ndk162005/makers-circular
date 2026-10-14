import json
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_, and_, String
from . import models, schemas

def get_dataset(db: Session, dataset_id: int):
    return db.query(models.Dataset).filter(models.Dataset.id == dataset_id).first()

def get_datasets(db: Session):
    datasets = db.query(models.Dataset).all()
    total = len(datasets)
    return datasets, total

def create_dataset(db: Session, dataset: schemas.DatasetBase):
    db_dataset = models.Dataset(**dataset.model_dump())
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    return db_dataset

def delete_dataset(db: Session, dataset_id: int):
    db_dataset = get_dataset(db, dataset_id)
    if db_dataset:
        db.delete(db_dataset)
        db.commit()
    return db_dataset

def get_record(db: Session, record_id: int):
    return db.query(models.Record).filter(models.Record.id == record_id).first()

def get_records(db: Session, dataset_id: int, page: int = 1, page_size: int = 50, search: str = None, maker: str = None, sort_by: str = None, sort_order: str = "asc", only_new: bool = False):
    query = db.query(models.Record).filter(models.Record.dataset_id == dataset_id)

    if maker:
        query = query.filter(func.json_extract(models.Record.data, '$.maker') == maker)

    if only_new:
        query = query.filter(func.json_extract(models.Record.data, '$.is_new') == True)

    if search:
        query = query.filter(func.cast(models.Record.data, String).ilike(f"%{search}%"))

    total = query.count()

    if sort_by in ["id", "created_at", "updated_at"]:
        sort_col = getattr(models.Record, sort_by)
    elif sort_by:
        sort_col = func.json_extract(models.Record.data, f"$.{sort_by}")
    else:
        sort_col = models.Record.id

    if str(sort_order).lower() == "desc":
        query = query.order_by(desc(sort_col), desc(models.Record.id))
    else:
        query = query.order_by(sort_col, models.Record.id)

    records = query.offset((page - 1) * page_size).limit(page_size).all()
    return records, total

def create_records_bulk(db: Session, dataset_id: int, records_data: list):
    records = [models.Record(dataset_id=dataset_id, data=data) for data in records_data]
    db.bulk_save_objects(records)
    db.commit()

def update_record(db: Session, record_id: int, data: dict):
    db_record = get_record(db, record_id)
    if db_record:
        db_record.data = data
        db.commit()
        db.refresh(db_record)
    return db_record

def delete_record(db: Session, record_id: int):
    db_record = get_record(db, record_id)
    if db_record:
        db.delete(db_record)
        db.commit()
    return db_record

def get_makers(db: Session, dataset_id: int):
    makers_query = db.query(
        func.json_extract(models.Record.data, '$.maker').label("maker"),
        func.count(models.Record.id).label("count")
    ).filter(
        models.Record.dataset_id == dataset_id,
        func.json_extract(models.Record.data, '$.maker') != None
    ).group_by("maker").order_by("maker").all()
    
    return [{"maker": row.maker, "count": row.count} for row in makers_query]

def get_stats(db: Session, dataset_id: int):
    total_records = db.query(models.Record).filter(models.Record.dataset_id == dataset_id).count()
    total_makers = len(get_makers(db, dataset_id))
    
    docs_with_links = db.query(models.Record).filter(
        models.Record.dataset_id == dataset_id,
        func.json_extract(models.Record.data, '$.document_link') != None,
        func.json_extract(models.Record.data, '$.document_link') != ""
    ).count()

    newly_added_records = db.query(models.Record).filter(
        models.Record.dataset_id == dataset_id,
        func.json_extract(models.Record.data, '$.is_new') == True
    ).count()

    return {
        "total_records": total_records,
        "total_makers": total_makers,
        "docs_with_links": docs_with_links,
        "records_with_dms": 0,
        "newly_added_records": newly_added_records
    }

def get_columns(db: Session, dataset_id: int):
    return db.query(models.ColumnDefinition).filter(models.ColumnDefinition.dataset_id == dataset_id).order_by(models.ColumnDefinition.position).all()

def add_column(db: Session, column: schemas.ColumnCreate):
    db_col = models.ColumnDefinition(**column.model_dump())
    db.add(db_col)
    db.commit()
    db.refresh(db_col)
    
    records = db.query(models.Record).filter(models.Record.dataset_id == column.dataset_id).all()
    for record in records:
        data = record.data.copy()
        data[column.name] = None
        record.data = data
    db.commit()
    return db_col

def rename_column(db: Session, column_id: int, column_update: schemas.ColumnUpdate):
    db_col = db.query(models.ColumnDefinition).filter(models.ColumnDefinition.id == column_id).first()
    if not db_col:
        return None
    old_name = db_col.name
    
    update_data = column_update.model_dump(exclude_unset=True)
    new_name = update_data.get("name", old_name)
    
    for key, value in update_data.items():
        setattr(db_col, key, value)
    
    if new_name != old_name:
        records = db.query(models.Record).filter(models.Record.dataset_id == db_col.dataset_id).all()
        for record in records:
            data = record.data.copy()
            if old_name in data:
                data[new_name] = data.pop(old_name)
                record.data = data
    
    db.commit()
    db.refresh(db_col)
    return db_col

def delete_column(db: Session, column_id: int):
    db_col = db.query(models.ColumnDefinition).filter(models.ColumnDefinition.id == column_id).first()
    if not db_col:
        return None
    
    col_name = db_col.name
    dataset_id = db_col.dataset_id
    
    db.delete(db_col)
    
    records = db.query(models.Record).filter(models.Record.dataset_id == dataset_id).all()
    for record in records:
        data = record.data.copy()
        if col_name in data:
            del data[col_name]
            record.data = data
            
    db.commit()
    return db_col
