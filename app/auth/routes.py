# auth/routes.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioOut, Token
from app.auth.auth_utils import pwd_context, criar_token_acesso
from app.database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)

security = HTTPBasic()


@router.post("/registrar_usuario",
            status_code=201,
            response_model=UsuarioOut,
            summary="Registrar novo usuário",
            description="""
                            Cria um novo usuário com `nome de usuário`, `senha` e `e-mail`.

                            - A senha é armazenada de forma segura usando hash (bcrypt).
                            - O e-mail e o nome de usuário devem ser únicos.
                            - Retorna uma mensagem de confirmação.
                            """,
            responses={
                400: {
                    "description": "Usuário ou e-mail já existe",
                    "content": {
                        "application/json": {
                            "example": {
                                "detail": "Usuário ou e-mail já existe"
                            }
                        }
                    }
                }
            }
            )
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registra um usuário com `usuario`, `senha` e `email`.
    A senha é automaticamente criptografada com bcrypt.
    """
    usuario_existente = db.query(Usuario).filter(
        (Usuario.usuario == usuario.usuario) | (Usuario.email == usuario.email)
    ).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Usuário ou e-mail já existe")

    senha_hash = pwd_context.hash(usuario.senha)
    novo_usuario = Usuario(
        usuario=usuario.usuario,
        senha_hash=senha_hash,
        email=usuario.email
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario


@router.post("/token",
            response_model=Token,
            summary="Realizar login e obter token JWT",
            description="""
            Realiza autenticação de um usuário via `HTTP Basic Auth`.

            - Retorna um token JWT se as credenciais estiverem corretas.
            - O token pode ser usado para acessar rotas protegidas (via `Authorization: Bearer <token>`).
            - A autenticação é feita por cabeçalho `Authorization: Basic`.
            """,
            responses={
                401: {
                    "description": "Credenciais inválidas",
                    "content": {
                        "application/json": {
                            "example": {
                                "detail": "Credenciais inválidas"
                            }
                        }
                    }
                }
            })

def login(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    Autentica usuário e retorna JWT.
    """
    usuario = db.query(Usuario).filter(Usuario.usuario == credentials.username).first()
    if not usuario or not pwd_context.verify(credentials.password, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    access_token = criar_token_acesso(data={"sub": usuario.usuario})
    return {"access_token": access_token, "token_type": "bearer"}
