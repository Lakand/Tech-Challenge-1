import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import TabelaScrap
from app.config import SCRAP_TIMEOUT_SECONDS


def scrap_tabela_embrapa(ano: str, opcao: str, subopcao: str, db: Session):
    url = f"http://vitibrasil.cnpuv.embrapa.br/index.php?ano={ano}&opcao=opt_{opcao}&subopcao=subopt_{subopcao}"
    
    try:
        response = requests.get(url, timeout=SCRAP_TIMEOUT_SECONDS)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        tabelas_html = soup.find_all('table', class_='tb_base tb_dados')

        if not tabelas_html:
            raise HTTPException(status_code=404, detail="Tabela não encontrada no site da Embrapa.")

        dados_tabela = []
        for tabela in tabelas_html:
            cabecalho = [th.get_text(strip=True) for th in tabela.find_all('th')]
            for tr in tabela.find_all('tr')[1:]:
                cols = [td.get_text(strip=True) for td in tr.find_all('td')]
                if cols:
                    dados_tabela.append(dict(zip(cabecalho, cols)))

        # Verifica se já existe no banco
        registro_existente = db.query(TabelaScrap).filter_by(
            ano=ano, opcao=opcao, subopcao=subopcao
        ).first()

        if not registro_existente:
            novo_registro = TabelaScrap(
                fonte=url, ano=ano, opcao=opcao, subopcao=subopcao, tabela=dados_tabela
            )
            db.add(novo_registro)
            db.commit()
            db.refresh(novo_registro)

        return {
            "fonte": url,
            "ano": ano,
            "opcao": opcao,
            "subopcao": subopcao,
            "tabela": dados_tabela
        }

    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):
        # fallback: tentar buscar no banco
        registro = db.query(TabelaScrap).filter_by(ano=ano, opcao=opcao, subopcao=subopcao).first()
        if registro:
            return {
                "fonte": registro.fonte + " (backup local)",
                "ano": registro.ano,
                "opcao": registro.opcao,
                "subopcao": registro.subopcao,
                "tabela": registro.tabela
            }
        raise HTTPException(status_code=503, detail="Site da Embrapa está fora do ar e não há backup local.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")
