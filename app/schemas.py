from typing import List, Dict, Any
from pydantic import BaseModel, EmailStr, constr, field_validator


# Schema para criação de usuário (entrada)
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


class TabelaScrapResponse(BaseModel):
    fonte: str
    ano: str
    opcao: str
    subopcao: str
    tabela: List[Dict[str, Any]]

    class Config:
        json_schema_extra  = {
            "example": {
                "fonte": "http://vitibrasil.cnpuv.embrapa.br/index.php?ano=2023&opcao=opt_02&subopcao=subopt_01",
                "ano": "2023",
                "opcao": "02",
                "subopcao": "01",
                "tabela": [
                    {
                        "Tipo de Uva": "Vinífera",
                        "Quantidade (toneladas)": "1234",
                        "Ano": "2023"
                    },
                    {
                        "Tipo de Uva": "Mesa",
                        "Quantidade (toneladas)": "5678",
                        "Ano": "2023"
                    }
                ]
            }
        }