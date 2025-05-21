import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import SCRAP_TIMEOUT_SECONDS
from app.models import TabelaScrap


def construir_url_embrapa(ano: str, opcao: str, subopcao: str) -> str:
    return (
        f"http://vitibrasil.cnpuv.embrapa.br/index.php?ano={ano}"
        f"&opcao=opt_{opcao}&subopcao=subopt_{subopcao}"
    )


def buscar_html_embrapa(url: str) -> str:
    response = requests.get(url, timeout=SCRAP_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.text


def extrair_dados_da_tabela(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    tabelas_html = soup.find_all("table", class_="tb_base tb_dados")

    if not tabelas_html:
        raise HTTPException(status_code=404, detail="Tabela não encontrada no site da Embrapa.")

    dados_tabela = []
    for tabela in tabelas_html:
        cabecalho = [th.get_text(strip=True) for th in tabela.find_all("th")]
        for tr in tabela.find_all("tr")[1:]:
            coluna = [td.get_text(strip=True) for td in tr.find_all("td")]
            if coluna:
                dados_tabela.append(dict(zip(cabecalho, coluna)))

    return dados_tabela


def salvar_tabela_no_banco(
    db: Session, url: str, ano: str, opcao: str, subopcao: str, dados: list
):
    registro_existente = db.query(TabelaScrap).filter_by(
        ano=ano, opcao=opcao, subopcao=subopcao
    ).first()

    if not registro_existente:
        novo_registro = TabelaScrap(
            fonte=url, ano=ano, opcao=opcao, subopcao=subopcao, tabela=dados
        )
        db.add(novo_registro)
        db.commit()
        db.refresh(novo_registro)


def scrap_tabela_embrapa(ano: str, opcao: str, subopcao: str, db: Session):
    url = construir_url_embrapa(ano, opcao, subopcao)

    try:
        html = buscar_html_embrapa(url)
        dados_tabela = extrair_dados_da_tabela(html)
        salvar_tabela_no_banco(db, url, ano, opcao, subopcao, dados_tabela)

        return {
            "fonte": url,
            "ano": ano,
            "opcao": opcao,
            "subopcao": subopcao,
            "tabela": dados_tabela,
        }

    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):
        registro = db.query(TabelaScrap).filter_by(
            ano=ano, opcao=opcao, subopcao=subopcao
        ).first()
        if registro:
            return {
                "fonte": registro.fonte + " (backup local)",
                "ano": registro.ano,
                "opcao": registro.opcao,
                "subopcao": registro.subopcao,
                "tabela": registro.tabela,
            }
        raise HTTPException(
            status_code=503,
            detail="Site da Embrapa está fora do ar e não há backup local.",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")
