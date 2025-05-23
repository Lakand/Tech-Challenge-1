from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.auth_utils import verificar_token
from app.database import get_db
from app.scrap.scraper import scrap_tabela_embrapa
from app.scrap.validators import converte_opcao_subopcao, validar_parametros_entrada
from app.schemas import TabelaScrapResponse


router = APIRouter(
    prefix="/scrap",
    tags=["Scraping"],
)


@router.get(
    "/tabela",
    response_model=TabelaScrapResponse,
    summary="Buscar dados de vitivinicultura do site da Embrapa",
    description="""
    Realiza scraping do site da Embrapa Viticultura e retorna os dados solicitados.  
    Caso o site esteja indisponível, tenta retornar os dados do banco local (fallback).

    - Autenticação JWT obrigatória.
    - Parâmetros aceitam tanto código quanto nomes normalizados (ex: '03' ou 'Processamento').
    """,
    responses={
        400: {
            "description": "Parâmetros de entrada inválidos.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Parâmetros de entrada (ano, opcao ou subopcao) inválidos."}}
            },
        },
        401: {
            "description": "Token JWT ausente ou inválido.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Token inválido"}}
            },
        },
        404: {
            "description": "Tabela não encontrada no site da Embrapa.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Tabela não encontrada no site da Embrapa."}
                }
            },
        },
        503: {
            "description": "Site da Embrapa fora do ar e sem backup local.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Site da Embrapa está fora do ar e não há backup local."
                    }
                }
            },
        }
    },
)
def scrap(
    ano: Optional[str] = Query(
        "2023", description="Ano dos dados (entre 1970 e 2023)", example="2023"
    ),
    opcao: Optional[str] = Query(
        "02",
        description="Código ou nome da opção (ex: 'Produção' ou '02')",
        example="02",
    ),
    subopcao: Optional[str] = Query(
        "01",
        description="Código ou nome da subopção (ex: 'Viníferas' ou '01')",
        example="01",
    ),
    usuario: str = Depends(verificar_token),
    db: Session = Depends(get_db),
):
    opcao_norm, subopcao_norm = converte_opcao_subopcao(opcao, subopcao)
    validar_parametros_entrada(ano, opcao_norm, subopcao_norm)

    return scrap_tabela_embrapa(ano, opcao_norm, subopcao_norm, db)
