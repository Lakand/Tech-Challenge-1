from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String, unique=True, index=True)
    senha_hash = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)

class TabelaScrap(Base):
    __tablename__ = "tabelas_scrap"
    id = Column(Integer, primary_key=True, index=True)
    fonte = Column(String, nullable=False)
    ano = Column(String, nullable=False)
    opcao = Column(String, nullable=False)
    subopcao = Column(String, nullable=False)
    tabela = Column(JSON, nullable=False)
