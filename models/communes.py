from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Communes(Base):
    __tablename__ = "communes"

    id = Column(Integer, primary_key=True, index=True)
    regions_id = Column(Integer)
    code = Column(String)
    description = Column(String)
    active = Column(Integer)
    author = Column(String)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())
