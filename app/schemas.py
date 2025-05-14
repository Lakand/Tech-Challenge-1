from typing import List, Dict, Any
from pydantic import BaseModel, EmailStr, constr, field_validator


# Schema para criação de usuário (entrada)
class UsuarioCreate(BaseModel):
    usuario: str
    senha: str
    email: EmailStr

    # Validação adicional para garantir o mínimo de caracteres
    @field_validator("usuario", "senha")
    def validar_minimo_caracteres(cls, valor, info):
        if info.field_name == "usuario" and len(valor) < 3:
            raise ValueError("O campo 'usuario' deve ter pelo menos 3 caracteres.")
        if info.field_name == "senha" and len(valor) < 6:
            raise ValueError("O campo 'senha' deve ter pelo menos 6 caracteres.")
        return valor


# Schema para o token JWT (retorno do login)
class Token(BaseModel):
    access_token: str
    token_type: str


# Schema para criação de scrap (entrada)
class TabelaScrapCreate(BaseModel):
    fonte: str
    ano: str
    opcao: str
    subopcao: str
    tabela: List[Dict[str, Any]]
