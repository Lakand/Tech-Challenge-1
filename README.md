## 🛠️ Como configurar o ambiente

1. Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env


app/
├── __init__.py
├── main.py                # Inicia a aplicação FastAPI
├── config.py              # Carrega variáveis do .env
├── database.py            # Engine e sessão SQLAlchemy
├── models.py              # Tabelas SQLAlchemy
├── schemas.py             # Schemas Pydantic
├── auth/                  # Tudo relacionado a autenticação
│   ├── __init__.py
│   ├── auth_utils.py      # Criação/verificação de tokens
│   └── routes.py          # Rotas de autenticação (/token, /criar_usuario)
├── scrap/                 # Tudo relacionado a scraping e validações
│   ├── __init__.py
│   ├── scraper.py         # Lógica de scraping e fallback
│   ├── validators.py      # Funções de validação de parâmetros
│   └── routes.py          # Rota GET /scrap
