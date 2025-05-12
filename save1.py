import re
import unicodedata
from typing import Optional

import jwt
import requests
from bs4 import BeautifulSoup
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta


SECRET_KEY = "chave_secreta_tech_challenge"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

security = HTTPBasic()

def criar_token_acesso(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verificar_token(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")



def normalizar_texto(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = re.sub(r'[\u0300-\u036f]', '', texto)
    return texto
 

def converte_opcao_subopcao(opcao: str, subopcao: str) -> tuple[str, str]:
    opcao_normalizada = normalizar_texto(opcao)
    subopcao_normalizada = normalizar_texto(subopcao)

    dicionario_opcao = {
        'producao': '02',
        'processamento': '03',
        'comercializacao': '04',
        'importacao': '05',
        'exportacao': '06',
    }

    codigo_opcao = dicionario_opcao.get(opcao_normalizada, opcao_normalizada)

    dicionario_subopcoes = {
        '03': {
            'viniferas': '01',
            'americanas e hibridas': '02',
            'uvas de mesa': '03',
            'sem classificacao': '04'
        },
        '05': {
            'vinhos de mesa': '01',
            'espumantes': '02',
            'uvas frescas': '03',
            'uvas passas': '04',
            'suco de uva': '05'
        },
        '06': {
            'vinhos de mesa': '01',
            'espumantes': '02',
            'uvas frescas': '03',
            'suco de uva': '04'
        }
    }

    if codigo_opcao in ['02', '04']:
        codigo_subopcao = '01'
    else:
        codigo_subopcao = dicionario_subopcoes.get(codigo_opcao, {}).get(subopcao_normalizada, subopcao_normalizada)

    return codigo_opcao, codigo_subopcao

def validar_ano(ano: str) -> bool:
    try:
        ano_int = int(ano)
    except ValueError:
        return False

    return 1970 <= ano_int <= 2023


def validar_opcao(opcao: str) -> bool:
    opcoes_validas = {'02', '03', '04', '05', '06'}
    return opcao in opcoes_validas


def validar_subopcao(opcao: str, subopcao: str) -> bool:
    subopcoes_validas = {
        '03': {'01', '02', '03', '04'},
        '05': {'01', '02', '03', '04', '05'},
        '06': {'01', '02', '03', '04'},
    }

    if opcao not in subopcoes_validas:
        return True

    return subopcao in subopcoes_validas[opcao]


app = FastAPI(
    title="Tech Challenge API",
    version="1.0.0",
    description="API para fazer o scrapping dos dados do site da embrapa viticultura",
)

@app.post("/login")
def login(credentials: HTTPBasicCredentials = Depends(security)):
    usuario = credentials.username
    senha = credentials.password

    # Autenticação simples (troque por validação real)
    if usuario != "admin" or senha != "1234":
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    access_token = criar_token_acesso(data={"sub": usuario})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/scrap")
async def scrap_data(
    ano: Optional[str] = '2023',
    opcao: Optional[str] = '02',
    subopcao: Optional[str] = '01',
    usuario: str = Depends(verificar_token)
):


    opcao_normalizada, subopcao_normalizada = converte_opcao_subopcao(opcao, subopcao)
    verificador_ano = validar_ano(ano)
    if not verificador_ano:
        return {"erro": "Ano inválido. Deve estar enmtre 1970 e 2023"}
    verificador_opcao = validar_opcao(opcao_normalizada)
    if not verificador_opcao:
        return {
            "erro": (
                "Opção inválida. Por favor, escolha entre o nome ou o número da opção."
                "Valores válidos: Produção (02), Processamento (03), Comercialização (04), "
                "Importação (05) e Exportação (06)."
            )
        }
    verificador_subopcao = validar_subopcao(opcao_normalizada, subopcao_normalizada)
    if not verificador_subopcao:
        return {
            "erro": (
                "Subopção inválida. Por favor, escolha entre o nome ou o número da subopção."
                "Valores válidos:\n "
                "Viníferas (01), Americanas e Híbridas (02), Uvas de Mesa (03), Sem Classificação (04) "
                "para a opção Processamento (03);\n\n "
                "Vinhos de mesa (01), Espumantes (02), Uvas frescas (03), Uvas passas (04), Suco de uva (05) "
                "para a opção Importação (05);\n\n "
                "Vinhos de mesa (01), Espumantes (02), Uvas frescas (03), Suco de uva (04)"
                "para a opção Exportação (06)."
            )
        }

    url = f'http://vitibrasil.cnpuv.embrapa.br/index.php?ano={ano}&opcao=opt_{opcao_normalizada}&subopcao=subopt_{subopcao_normalizada}'
    try:
        # Faz a requisição para a URL fornecida
        response = requests.get(url)
        response.raise_for_status()  # Gera exceção se a resposta for erro
        soup = BeautifulSoup(response.text, "html.parser")

        # Encontra todas as tabelas com a classe 'tb_base tb_dados'
        tabela = soup.find_all('table', class_= 'tb_base tb_dados')

        if not tabela:
            return {"erro": "Tabela não encontrada"}
        
        # Inicializa a lista de dados
        dados_tabela = []

        # Para cada tabela encontrada (geralmente terá apenas uma, mas pode ser mais)
        for t in tabela:
            # Encontrando os cabeçalhos da tabela (primeira linha <th>)
            cabecalho = [th.get_text(strip=True) for th in t.find_all('th')]

            # Percorre todas as linhas da tabela (exceto o cabeçalho)
            for tr in t.find_all('tr')[1:]:  # Ignora a primeira linha (cabeçalho)
                cols = [td.get_text(strip=True) for td in tr.find_all('td')]
                if cols:  # Se há dados na linha
                    dados_tabela.append(dict(zip(cabecalho, cols)))
        
        # Retorna os dados extraídos como JSON"""
        return {
            "fonte": url,
            "ano": ano,
            "opcao": opcao_normalizada,
            "subopcao": subopcao_normalizada,
            "tabela": dados_tabela
        }        


    except Exception as e:
        return {"erro": str(e)}