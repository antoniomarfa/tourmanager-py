from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Regions(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String)
    code_internal = Column(String)
    description = Column(String)
    position = Column(Integer)
    active = Column(Integer)
    author = Column(String)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())