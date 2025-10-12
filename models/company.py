from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, index=True)
    rut = Column(String)
    razonsocial = Column(String)
    nomfantasia = Column(String)
    direccion = Column(String)
    comuna_id = Column(Integer)
    region_id = Column(Integer)
    rutreplegal = Column(String)
    nomreplegal = Column(String)
    nombrecontacto1 = Column(String)
    fonocontacto1 = Column(String)
    emailcontacto1 = Column(String)
    nombrecontacto2 = Column(String)
    fonocontacto2 = Column(String)
    emailcontacto2 = Column(String)
    contrato = Column(String)
    contrato_vg = Column(String)
    website = Column(String)
    identificador = Column(String)
    email = Column(String)
    schema_name = Column(String)
    iniciooperacion= Column(DateTime)
    plancode_id= Column(Integer)
    additionaluser= Column(Integer)
    maxusers= Column(Integer)
    maxquote= Column(Integer)
    maxsales= Column(Integer)
    terminoscondiciones= Column(Integer)
    politicasdeuso= Column(Integer)
    active= Column(Integer)
    author = Column(String)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())
