import os
import pandas as pd
import openpyxl
from fastapi import HTTPException
from sqlalchemy.orm import Session
from .. import models

def validate_file(file):
    filename = file.filename
    if not filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported")
    return filename

def parse_excel(file_path):
    wb = openpyxl.load_workbook(file_path, read_only=True)
    return wb.sheetnames

def normalize_column_name(col: str) -> str:
    if not isinstance(col, str):
        return "unnamed_column"
    return col.strip().lower().replace(" ", "_").replace("\n", "_")

def generate_preview(file_path, sheet_name=None):
    sheet_names = parse_excel(file_path)
    if not sheet_name:
        sheet_name = sheet_names[0]
        
    df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=10)
    df_all = pd.read_excel(file_path, sheet_name=sheet_name, usecols=[0])
    row_count = len(df_all)
    
    columns = [normalize_column_name(str(c)) for c in df.columns]
    df.columns = columns
    # Exclude _id, id, and dms
    valid_cols = [c for c in columns if c not in ['_id', 'id', 'dms']]
    df = df[valid_cols]
    df = df.replace({float('nan'): None})
    preview_data = df.to_dict(orient='records')
    
    return {
        "sheet_names": sheet_names,
        "columns": valid_cols,
        "row_count": row_count,
        "preview_data": preview_data
    }

def import_data(file_path, sheet_name, dataset_id, db: Session):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    original_columns = list(df.columns)
    normalized_columns = [normalize_column_name(str(c)) for c in original_columns]
    df.columns = normalized_columns
    
    # Exclude _id, id, and dms
    valid_columns = [c for c in normalized_columns if c not in ['_id', 'id', 'dms']]
    df = df[valid_columns]
    df = df.replace({float('nan'): None})
    
    for i, col_name in enumerate(valid_columns):
        col_def = models.ColumnDefinition(
            dataset_id=dataset_id,
            name=col_name,
            data_type="text",
            position=i
        )
        db.add(col_def)
    db.commit()
    
    records_data = df.to_dict(orient='records')
    records = [models.Record(dataset_id=dataset_id, data=data) for data in records_data]
    
    db.bulk_save_objects(records)
    
    dataset = db.query(models.Dataset).filter(models.Dataset.id == dataset_id).first()
    dataset.row_count = len(records_data)
    dataset.column_count = len(valid_columns)
    dataset.column_names = valid_columns
    db.commit()
    
    return dataset
