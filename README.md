# Tech Challenge - API de Scraping da Embrapa

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![API Status](https://img.shields.io/badge/API-Online-brightgreen.svg)](https://tech-challenge-api-embrapa.onrender.com/docs)

API REST desenvolvida em FastAPI que realiza scraping de tabelas do site da Embrapa Viticultura. Inclui autenticação JWT, sistema de fallback com cache local em banco de dados SQLite e validação robusta de parâmetros.

## 🌐 **API Online**

🚀 **Acesse a API em produção:** https://tech-challenge-api-embrapa.onrender.com

📖 **Documentação interativa:** https://tech-challenge-api-embrapa.onrender.com/docs

## 🚀 Funcionalidades

- **Scraping Inteligente**: Extração de dados do site da Embrapa com fallback automático
- **Autenticação JWT**: Sistema completo de registro e login de usuários
- **Cache Local**: Backup automático dos dados em SQLite para alta disponibilidade
- **Validação Flexível**: Aceita códigos numéricos ou nomes descritivos (com/sem acentos)
- **API Documentada**: Documentação interativa automática via Swagger/OpenAPI

---

## 🛠 Tecnologias Utilizadas

- **Python 3.11+**
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy + SQLite** - ORM e banco de dados
- **JWT (PyJWT)** - Autenticação segura
- **Bcrypt** - Hash seguro de senhas
- **BeautifulSoup4** - Web scraping
- **Uvicorn** - Servidor ASGI
- **Pydantic** - Validação de dados

---

## 📁 Estrutura do Projeto

```
app/
├── auth/                  # Módulo de autenticação
│   ├── __init__.py
│   ├── auth_utils.py      # Utilitários JWT e hash de senha
│   └── routes.py          # Rotas de autenticação
│
├── scrap/                 # Módulo de scraping
│   ├── __init__.py
│   ├── scraper.py         # Lógica de scraping e fallback
│   ├── validators.py      # Validação e normalização de parâmetros
│   └── routes.py          # Rotas de scraping
│
├── config.py              # Configurações e variáveis de ambiente
├── database.py            # Configuração do banco SQLite
├── models.py              # Modelos SQLAlchemy
├── schemas.py             # Schemas Pydantic para validação
└── main.py                # Aplicação principal FastAPI
```

---

## 🖼️ Diagrama do projeto

![Diagrama do projeto](images/diagrama_tech_challenge.png)

---

## 📊 Fonte de Dados

Dados extraídos diretamente do site oficial da [Embrapa Vitivinicultura](http://vitibrasil.cnpuv.embrapa.br), incluindo informações sobre:

- **Produção** de uvas
- **Processamento** por tipo de uva
- **Comercialização** no mercado interno
- **Importação/Exportação** de produtos vitivinícolas

---

## ⚡ Instalação e Execução

### Pré-requisitos
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

### 1. Clone o repositório
```bash
git clone https://github.com/seuusuario/tech-challenge.git
cd tech-challenge
```

### 2. Crie e ative o ambiente virtual
```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:
```env
SECRET_KEY=sua_chave_secreta_muito_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./scrap_embrapa.db
SCRAP_TIMEOUT_SECONDS=10
```

### 5. Execute o servidor
```bash
uvicorn app.main:app --reload
```

A API estará disponível em: `http://localhost:8000`

> **📝 Nota:** Na primeira execução, o banco SQLite e as tabelas são criados automaticamente.

### 🌐 Ou acesse a versão online

Prefere testar sem instalar? Use nossa **API em produção**:
- **Base URL:** `https://tech-challenge-api-embrapa.onrender.com`
- **Documentação:** `https://tech-challenge-api-embrapa.onrender.com/docs`

---

## 🔐 Autenticação

A API utiliza autenticação JWT com as seguintes características:

- **Registro**: Criação de usuários com hash seguro de senhas (bcrypt)
- **Login**: Autenticação via HTTP Basic Auth
- **Proteção**: Rotas protegidas requerem `Authorization: Bearer <token>`
- **Expiração**: Tokens configuráveis (padrão: 60 minutos)

---

## 📋 Endpoints da API

### Autenticação

| Método | Endpoint              | Descrição                    | Autenticação |
|--------|-----------------------|------------------------------|--------------|
| POST   | `/auth/registrar_usuario` | Criar novo usuário           | ❌           |
| POST   | `/auth/token`         | Login e obtenção de token    | Basic Auth   |

### Scraping

| Método | Endpoint        | Descrição                           | Autenticação |
|--------|-----------------|-------------------------------------|--------------|
| GET    | `/scrap/tabela` | Scraping de dados da Embrapa        | Bearer Token |

---

## 📖 Guia de Uso dos Endpoints

### 🔹 POST `/auth/registrar_usuario`

Registra um novo usuário no sistema.

#### **Regras de Validação:**

| Campo    | Regra                                    | Exemplo Válido     | Exemplo Inválido |
|----------|------------------------------------------|--------------------|------------------|
| **usuario** | • Mínimo: 3 caracteres<br>• Deve ser único no sistema | `"usuario1"`       | `"ab"` (muito curto) |
| **senha**   | • Mínimo: 6 caracteres                    | `"senha123"`       | `"123"` (muito curta) |
| **email**   | • Formato de e-mail válido<br>• Deve ser único no sistema | `"user@email.com"` | `"email-inválido"` |

**Body (JSON):**
```json
{
  "usuario": "usuario1",
  "senha": "senha123",
  "email": "usuario@email.com"
}
```

**Resposta de Sucesso (201):**
```json
{
  "id": 1,
  "usuario": "usuario1",
  "email": "usuario@email.com"
}
```

### 🔹 POST `/auth/token`

Autentica usuário e retorna token JWT.

**Headers:**
```
Authorization: Basic <base64(usuario:senha)>
```

**Resposta de Sucesso (200):**
```json
{
  "acesso_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "tipo_token": "bearer"
}
```

### 🔹 GET `/scrap/tabela`

Realiza scraping dos dados da Embrapa ou retorna dados do cache local.

**Headers:**
```
Authorization: Bearer <seu_token>
```

**Query Parameters:**

| Parâmetro | Tipo   | Obrigatório | Descrição                              | Exemplo     |
|-----------|--------|-------------|----------------------------------------|-------------|
| `ano`     | string | ✅          | Ano dos dados (1970-2024)             | `"2023"`    |
| `opcao`   | string | ✅          | Código ou nome da categoria principal  | `"03"` ou `"Processamento"` |
| `subopcao`| string | ✅          | Código ou nome da subcategoria         | `"01"` ou `"Viníferas"` |

**Exemplo de Chamada:**
```
GET /scrap/tabela?ano=2023&opcao=Processamento&subopcao=Viníferas
```

---

## 📝 Parâmetros Detalhados

### 🎯 Parâmetro `ano`
- **Formato:** String representando o ano
- **Intervalo:** 1970 a 2024
- **Exemplo:** `"2023"`

### 🎯 Parâmetro `opcao`

Aceita código numérico ou nome (case-insensitive, com/sem acentos):

| Nome              | Código |
|-------------------|--------|
| Produção          | `02`   |
| Processamento     | `03`   |
| Comercialização   | `04`   |
| Importação        | `05`   |
| Exportação        | `06`   |

### 🎯 Parâmetro `subopcao`

Varia conforme a `opcao` selecionada:

#### Para Processamento (`03`)
| Nome                          | Código |
|-------------------------------|--------|
| Viníferas                     | `01`   |
| Americanas e Híbridas         | `02`   |
| Uvas de Mesa                  | `03`   |
| Sem Classificação             | `04`   |

#### Para Importação (`05`)
| Nome            | Código |
|------------------|--------|
| Vinhos de Mesa   | `01`   |
| Espumantes       | `02`   |
| Uvas Frescas     | `03`   |
| Uvas Passas      | `04`   |
| Suco de Uva      | `05`   |

#### Para Exportação (`06`)
| Nome            | Código |
|------------------|--------|
| Vinhos de Mesa   | `01`   |
| Espumantes       | `02`   |
| Uvas Frescas     | `03`   |
| Suco de Uva      | `04`   |

> **💡 Dica:** Para Produção e Comercialização, use `subopcao="01"` ou omita o parâmetro.

---

## 🧪 Testando com Postman

> **💡 Dica:** Use a API online em `https://tech-challenge-api-embrapa.onrender.com` ou sua instalação local.

### 1. Registrar Usuário
```
POST https://tech-challenge-api-embrapa.onrender.com/auth/registrar_usuario
Content-Type: application/json

{
  "usuario": "teste",
  "senha": "senha123",
  "email": "teste@email.com"
}
```

### 2. Obter Token
```
POST https://tech-challenge-api-embrapa.onrender.com/auth/token
Authorization: Basic dGVzdGU6c2VuaGExMjM=  # base64(teste:senha123)
```

### 3. Fazer Scraping
```
GET https://tech-challenge-api-embrapa.onrender.com/scrap/tabela?ano=2023&opcao=03&subopcao=01
Authorization: Bearer <seu_token_aqui>
```

---

## 🔄 Sistema de Fallback

A API implementa um sistema inteligente de fallback:

1. **Tentativa Primária**: Scraping direto do site da Embrapa
2. **Cache Local**: Se o site estiver indisponível, busca dados salvos no SQLite
3. **Erro 503**: Apenas se não houver dados nem online nem no cache

Isso garante **alta disponibilidade** mesmo quando o site oficial estiver fora do ar.

---

## 📚 Documentação Interativa

### 🌐 Online (Recomendado)
- **Swagger UI**: https://tech-challenge-api-embrapa.onrender.com/docs
- **ReDoc**: https://tech-challenge-api-embrapa.onrender.com/redoc

### 💻 Local
Após iniciar o servidor localmente:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

Ambas oferecem interface completa para testar todos os endpoints diretamente no navegador.

---

## ⚠️ Códigos de Erro

| Código | Descrição                                    |
|--------|----------------------------------------------|
| 400    | Parâmetros inválidos                        |
| 401    | Token JWT ausente, inválido ou expirado     |
| 404    | Tabela não encontrada no site da Embrapa    |
| 503    | Site fora do ar sem backup local disponível |

---

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👤 Autor

**Celso Gabriel Vieira Ribeiro Lopes**
- Email: c.gabriel.vieira@hotmail.com
- GitHub: [@Lakand](https://github.com/Lakand)

---

## 🙏 Agradecimentos

- [Embrapa Vitivinicultura](http://vitibrasil.cnpuv.embrapa.br) pelos dados públicos
- Comunidade FastAPI pela excelente documentação
- Colaboradores e revisores do projeto