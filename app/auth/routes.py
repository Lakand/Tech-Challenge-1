# auth/routes.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Usuario
from app.schemas import UsuarioCreate, Token
from app.auth.auth_utils import pwd_context, criar_token_acesso

router = APIRouter()

security = HTTPBasic()

# Dependência de banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/criar_usuario", status_code=201)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
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


@router.post("/token", response_model=Token)
def login(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.usuario == credentials.username).first()
    if not usuario or not pwd_context.verify(credentials.password, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    access_token = criar_token_acesso(data={"sub": usuario.usuario})
    return {"access_token": access_token, "token_type": "bearer"}
