import re
import unicodedata

from fastapi import HTTPException


def normalizar_texto(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = re.sub(r"[\u0300-\u036f]", "", texto)
    return texto


def converte_opcao_subopcao(opcao: str, subopcao: str) -> tuple[str, str]:
    opcao_normalizada = normalizar_texto(opcao)
    subopcao_normalizada = normalizar_texto(subopcao)

    dicionario_opcao = {
        "producao": "02",
        "processamento": "03",
        "comercializacao": "04",
        "importacao": "05",
        "exportacao": "06",
    }

    codigo_opcao = dicionario_opcao.get(opcao_normalizada, opcao_normalizada)

    dicionario_subopcoes = {
        "03": {
            "viniferas": "01",
            "americanas e hibridas": "02",
            "uvas de mesa": "03",
            "sem classificacao": "04",
        },
        "05": {
            "vinhos de mesa": "01",
            "espumantes": "02",
            "uvas frescas": "03",
            "uvas passas": "04",
            "suco de uva": "05",
        },
        "06": {
            "vinhos de mesa": "01",
            "espumantes": "02",
            "uvas frescas": "03",
            "suco de uva": "04",
        },
    }

    if codigo_opcao in ["02", "04"]:
        codigo_subopcao = "01"
    else:
        codigo_subopcao = dicionario_subopcoes.get(
            codigo_opcao, {}
        ).get(subopcao_normalizada, subopcao_normalizada)

    return codigo_opcao, codigo_subopcao


def validar_parametros_entrada(ano: str, opcao: str, subopcao: str) -> None:
    if not validar_ano(ano):
        raise HTTPException(
            status_code=400, detail="Ano inválido. Deve estar entre 1970 e 2024."
        )

    if not validar_opcao(opcao):
        raise HTTPException(
            status_code=400,
            detail=(
                "Opção inválida. Use: Produção (02), Processamento (03), "
                "Comercialização (04), Importação (05), Exportação (06)."
            ),
        )

    if not validar_subopcao(opcao, subopcao):
        mensagens_erro_subopcao = {
            "03": (
                "Subopção inválida para Processamento (03). Use o nome ou o número "
                "para subopção desejada: Viníferas (01), Americanas e Híbridas (02), "
                "Uvas de Mesa (03), Sem Classificação (04)."
            ),
            "05": (
                "Subopção inválida para Importação (05). Use o nome ou o número "
                "para subopção desejada: Vinhos de Mesa (01), Espumantes (02), "
                "Uvas Frescas (03), Uvas Passas (04), Suco de Uva (05)."
            ),
            "06": (
                "Subopção inválida para Exportação (06). Use o nome ou o número "
                "para subopção desejada: Vinhos de Mesa (01), Espumantes (02), "
                "Uvas Frescas (03), Suco de Uva (04)."
            ),
    }
        if opcao in mensagens_erro_subopcao:
            raise HTTPException(status_code=400, detail=mensagens_erro_subopcao[opcao])


def validar_ano(ano: str) -> bool:
    try:
        ano_int = int(ano)
        return 1970 <= ano_int <= 2024
    except ValueError:
        return False


def validar_opcao(opcao: str) -> bool:
    return opcao in {"02", "03", "04", "05", "06"}


def validar_subopcao(opcao: str, subopcao: str) -> bool:
    subopcoes_validas = {
        "03": {"01", "02", "03", "04"},
        "05": {"01", "02", "03", "04", "05"},
        "06": {"01", "02", "03", "04"},
    }
    if opcao not in subopcoes_validas:
        return True
    return subopcao in subopcoes_validas[opcao]
