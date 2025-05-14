from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.auth.auth_utils import verificar_token
from app.scrap.validators import converte_opcao_subopcao, validar_parametros_entrada
from app.scrap.scraper import scrap_tabela_embrapa

router = APIRouter()

# Dependência de banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/scrap")
def scrap(
    ano: Optional[str] = '2023',
    opcao: Optional[str] = '02',
    subopcao: Optional[str] = '01',
    usuario: str = Depends(verificar_token),
    db: Session = Depends(get_db)
):
    opcao_norm, subopcao_norm = converte_opcao_subopcao(opcao, subopcao)
    validar_parametros_entrada(ano, opcao_norm, subopcao_norm)

    return scrap_tabela_embrapa(ano, opcao_norm, subopcao_norm, db)
