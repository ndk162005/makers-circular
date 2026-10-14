from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String, nullable=False)
    worksheet_name = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    column_names = Column(JSON)
    status = Column(String, default="active")
    
    records = relationship("Record", back_populates="dataset", cascade="all, delete-orphan")
    columns = relationship("ColumnDefinition", back_populates="dataset", cascade="all, delete-orphan")

class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    dataset = relationship("Dataset", back_populates="records")

class ColumnDefinition(Base):
    __tablename__ = "column_definitions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    name = Column(String, nullable=False)
    data_type = Column(String, default="text")
    position = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    dataset = relationship("Dataset", back_populates="columns")
