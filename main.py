import re
import unicodedata
from datetime import datetime, timedelta
from typing import Optional

import jwt
import requests
from bs4 import BeautifulSoup
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, HTTPBasicCredentials, HTTPBasic
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext


SECRET_KEY = "chave_secreta_tech_challenge"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

DATABASE_URL = "sqlite:///./usuarios.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

security = HTTPBasic()

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String, unique=True, index=True)
    senha_hash = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)

Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def criar_token_acesso(data: dict, expires_delta: timedelta = None):
    # Cria um token de acesso com os dados fornecidos e uma data de expiração
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(token: str = Depends(oauth2_scheme)) -> str:
    # Verifica a validade do token JWT e retorna o nome de usuário associado
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
    # Normaliza o texto para facilitar a comparação
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = re.sub(r'[\u0300-\u036f]', '', texto)
    return texto
 

def converte_opcao_subopcao(opcao: str, subopcao: str) -> tuple[str, str]:
    # Converte a opção e subopção para seus respectivos códigos
    # Se a opção ou subopção não estiverem no dicionário, retorna o próprio valor
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

def validar_parametros_entrada(ano: str, opcao: str, subopcao: str) -> None:
    # Verifica se os dados de entrada estão corretos
    # Se não estiverem, lança uma exceção HTTP 400
    opcao_normalizada, subopcao_normalizada = converte_opcao_subopcao(opcao, subopcao)

    if not validar_ano(ano):
        raise HTTPException(status_code=400, detail="Ano inválido. Deve estar entre 1970 e 2023.")

    if not validar_opcao(opcao_normalizada):
        raise HTTPException(
            status_code=400,
            detail=(
                "Opção inválida. Por favor, escolha entre um dos nomes ou números na variável opção. "
                "Valores válidos: Produção (02), Processamento (03), Comercialização (04), "
                "Importação (05) e Exportação (06)."
            )
        )
    
    if not validar_subopcao(opcao_normalizada, subopcao_normalizada):
        mensagens_erro_subopcao = {
            '03': (
                "Subopção inválida para 'Produção (03)'. "
                "Você pode informar o nome da subopção (ex: 'Viníferas') ou o código "
                "correspondente (ex: '01'). Opções válidas: Viníferas (01), Americanas "
                "e Híbridas (02), Uvas de Mesa (03), Sem Classificação (04)."
            ),
            '05': (
                "Subopção inválida para 'Distribuição (05)'. "
                "Você pode informar o nome da subopção (ex: 'Espumantes') ou o código "
                "correspondente (ex: '02'). Opções válidas: Vinhos de mesa (01), "
                "Espumantes (02), Uvas frescas (03), Uvas passas (04), Suco de uva (05)."
            ),
            '06': (
                "Subopção inválida para 'Exportação (06)'. "
                "Você pode informar o nome da subopção (ex: 'Suco de uva') ou o código "
                "correspondente (ex: '04'). Opções válidas: Vinhos de mesa (01), "
                "Espumantes (02), Uvas frescas (03), Suco de uva (04)."
            )
        }
        if opcao_normalizada in mensagens_erro_subopcao:
            raise HTTPException(status_code=400, detail=mensagens_erro_subopcao[opcao_normalizada])

def validar_ano(ano: str) -> bool:
    # Verifica se o ano está entre 1970 e 2023
    try:
        ano_int = int(ano)
    except ValueError:
        return False

    return 1970 <= ano_int <= 2023


def validar_opcao(opcao: str) -> bool:
    # Verifica se a opção é válida
    opcoes_validas = {'02', '03', '04', '05', '06'}
    return opcao in opcoes_validas


def validar_subopcao(opcao: str, subopcao: str) -> bool:
    # Verifica se a subopção é válida para a opção dada
    subopcoes_validas = {
        '03': {'01', '02', '03', '04'},
        '05': {'01', '02', '03', '04', '05'},
        '06': {'01', '02', '03', '04'},
    }

    if opcao not in subopcoes_validas:
        return True

    return subopcao in subopcoes_validas[opcao]


# Schemas Pydantic
class UsuarioCreate(BaseModel):
    usuario: str
    senha: str
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

# Dependência de sessão

def get_db():
    # Cria uma nova sessão de banco de dados
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



app = FastAPI(
    title="Tech Challenge API",
    version="1.0.0",
    description="API para fazer o scrapping dos dados do site da embrapa viticultura",
)


@app.post("/criar_usuario", status_code=201)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # Cria um novo usuário no banco de dados
    # Verifica se o usuário já existe
    usuario_existente = db.query(Usuario).filter(
        (Usuario.usuario == usuario.usuario) | (Usuario.email == usuario.email)
    ).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Usuário ou e-mail já existe")
    senha_hash = pwd_context.hash(usuario.senha)
    novo_usuario = Usuario(usuario=usuario.usuario, senha_hash=senha_hash, email=usuario.email)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return {"mensagem": "Usuário criado com sucesso"}

# Rota de login

@app.post("/token", response_model=Token)
def login(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    # Verifica as credenciais do usuário
    # Se as credenciais forem válidas, gera um token de acesso
    usuario = db.query(Usuario).filter(Usuario.usuario == credentials.username).first()
    if not usuario or not pwd_context.verify(credentials.password, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    access_token = criar_token_acesso(data={"sub": usuario.usuario})

    return {"access_token": access_token, "token_type": "bearer"}



@app.get("/scrap")
async def scrap_data(
    ano: Optional[str] = '2023',
    opcao: Optional[str] = '02',
    subopcao: Optional[str] = '01',
    usuario: str = Depends(verificar_token)
):

    opcao_normalizada, subopcao_normalizada = converte_opcao_subopcao(opcao, subopcao)
    validar_parametros_entrada(ano, opcao_normalizada, subopcao_normalizada)

    url = f'http://vitibrasil.cnpuv.embrapa.br/index.php?ano={ano}&opcao=opt_{opcao_normalizada}&subopcao=subopt_{subopcao_normalizada}'
    try:
        # Faz a requisição para a URL fornecida
        response = requests.get(url)
        response.raise_for_status()  # Gera exceção se a resposta for erro
        soup = BeautifulSoup(response.text, "html.parser")

        # Encontra todas as tabelas com a classe 'tb_base tb_dados'
        tabela = soup.find_all('table', class_= 'tb_base tb_dados')

        if not tabela:
            raise HTTPException(status_code=404, detail="Tabela não encontrada")
        
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


    except requests.exceptions.RequestException as e:
        # Captura erros gerais relacionados à requisição (rede, timeout, etc.)
        raise HTTPException(status_code=500, detail=f"Erro na requisição: {str(e)}")
    
    except requests.exceptions.HTTPError as e:
        # Captura erros específicos de status HTTP (erro 404, 500, etc.)
        raise HTTPException(status_code=response.status_code, detail=f"Erro HTTP: {response.status_code}")
    
    except Exception as e:
        # Captura qualquer outra exceção não prevista
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")