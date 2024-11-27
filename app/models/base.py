# app/models/base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr

class CustomBase:
    @declared_attr
    def __tablename__(cls):
        # Convert CamelCase to snake_case for table names
        return ''.join(['_' + c.lower() if c.isupper() else c for c in cls.__name__]).lstrip('_')
    
    # Add common columns or methods here if needed

Base = declarative_base(cls=CustomBase)