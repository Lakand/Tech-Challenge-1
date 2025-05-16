from typing import Any, Dict, List

from pydantic import BaseModel, EmailStr, field_validator


class UsuarioCreate(BaseModel):
    usuario: str
    senha: str
    email: EmailStr

    @field_validator("usuario", "senha")
    def validar_minimo_caracteres(cls, valor, info):
        if info.field_name == "usuario" and len(valor) < 3:
            raise ValueError("O campo 'usuario' deve ter pelo menos 3 caracteres.")
        if info.field_name == "senha" and len(valor) < 6:
            raise ValueError("O campo 'senha' deve ter pelo menos 6 caracteres.")
        return valor

    class Config:
        json_schema_extra = {
            "example": {
                "usuario": "usuario1",
                "senha": "senha123",
                "email": "usuario1@email.com",
            }
        }


class UsuarioOut(BaseModel):
    id: int
    usuario: str
    email: EmailStr

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "usuario": "usuario1",
                "email": "usuario1@email.com",
            }
        }


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }


class TabelaScrapCreate(BaseModel):
    fonte: str
    ano: str
    opcao: str
    subopcao: str
    tabela: List[Dict[str, Any]]


class TabelaScrapResponse(BaseModel):
    fonte: str
    ano: str
    opcao: str
    subopcao: str
    tabela: List[Dict[str, Any]]

    class Config:
        json_schema_extra = {
            "example": {
                "fonte": "http://vitibrasil.cnpuv.embrapa.br/index.php?ano=2023&opcao=opt_02&subopcao=subopt_01",
                "ano": "2023",
                "opcao": "02",
                "subopcao": "01",
                "tabela": [
                    {
                        "Tipo de Uva": "Vinífera",
                        "Quantidade (toneladas)": "1234",
                        "Ano": "2023",
                    },
                    {
                        "Tipo de Uva": "Mesa",
                        "Quantidade (toneladas)": "5678",
                        "Ano": "2023",
                    },
                ],
            }
        }
