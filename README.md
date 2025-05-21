# Tech Challenge - API de Scraping da Embrapa

API REST desenvolvida em FastAPI que realiza scraping de tabelas do site da Embrapa Viticultura. Inclui autenticação JWT, fallback com cache local em banco de dados.

---

## Tecnologias utilizadas

- Python 3.11
- FastAPI
- SQLAlchemy + SQLite
- JWT (via PyJWT)
- Bcrypt (para hash de senha)
- BeautifulSoup (web scraping)
- Uvicorn (servidor ASGI)

---

## Estrutura do projeto

```
app/
├── auth/                  # Rotas e utilitários de autenticação
│   ├── __init__.py
│   ├── auth_utils.py      # Funções de criação e verificação de tokens, hash de senha
│   └── routes.py          # Rotas de autenticação (/auth/usuario, /auth/token)
│
├── scrap/                 # Rotas, scraping e validações
│   ├── __init__.py
│   ├── scraper.py         # Lógica principal de scraping e fallback
│   ├── validators.py      # Validação de parâmetros de entrada
│   └── routes.py          # Rotas para scraping (/scrap/tabela)
│
├── database.py            # Configuração e sessão do banco de dados SQLite
├── config.py              # Leitura de variáveis do ambiente (.env)
├── schemas.py             # Schemas Pydantic para validação de dados
├── models.py              # Modelos SQLAlchemy representando tabelas do DB
└── main.py                # Entrada principal da aplicação FastAPI
```

---
## Fonte de dados

Dados obtidos diretamente do site da [Embrapa Vitivinicultura](http://vitibrasil.cnpuv.embrapa.br).

---

## Como rodar o projeto

### 1. Clone o repositório
```bash
git clone https://github.com/seuusuario/tech-challenge.git
cd tech-challenge
```

### 2. Crie o ambiente virtual e ative
```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Crie o arquivo `.env` com base no `.env.example`
```bash
cp .env.example .env
```

### 5. Rode o servidor
```bash
uvicorn app.main:app --reload
```
Observação:
Ao iniciar o servidor pela primeira vez, o banco de dados SQLite e as tabelas são criados automaticamente pelo SQLAlchemy com base nos modelos definidos em models.py.

---

## Variáveis de ambiente necessárias

```env
SECRET_KEY=suachavesecreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./scrap_embrapa.db
SCRAP_TIMEOUT_SECONDS=10
```

---

## Autenticação

- O login é feito com `HTTP Basic Auth` via endpoint `/auth/token`.
- As rotas protegidas exigem `Authorization: Bearer <seu_token>` no cabeçalho.

---

## Endpoints principais

| Método | Rota                 | Descrição                                     |
|--------|----------------------|-----------------------------------------------|
| POST   | `/auth/usuario`      | Criação de novo usuário                       |
| POST   | `/auth/token`        | Login e geração de token JWT                  |
| GET    | `/scrap/tabela`      | Realiza scraping da Embrapa (requer token)    |

---

##  Detalhes das Rotas

###  POST `/auth/usuario`

Cria um novo usuário no sistema com hash de senha seguro.

* **Body (JSON):**

```json
{
  "usuario": "usuario1",
  "senha": "senha123",
  "email": "usuario@email.com"
}
```

* **Resposta:**

```json
{
  "id": 1,
  "usuario": "usuario1",
  "email": "usuario@email.com"
}
```

###  POST `/auth/token`

Gera o token JWT com base nas credenciais do usuário (HTTP Basic Auth). Esse usuário deve ser criado na rota `/auth/usuario`.

* **Autenticação:** Authorization: Basic `<base64(usuario:senha)>`
* **Resposta:**

```json
{
  "access_token": "<token>",
  "token_type": "bearer"
}
```

###  GET `/scrap/tabela`

- Realiza scraping com base em três parâmetros obrigatórios: `ano`, `opcao` e `subopcao`. 
- Quando uma tabela é consultada pela primeira vez, seus dados são extraídos do site e armazenados localmente no banco de dados.
- Em chamadas futuras, se o site da Embrapa estiver indisponível, a API busca no banco de dados se a tabela correspondente já foi salva anteriormente.
- Caso os dados existam no banco, eles são retornados como fallback automático — garantindo maior disponibilidade da API mesmo em caso de instabilidade externa.

* **Headers:** Authorization: Bearer `<token>`
* **Query Params:**

  * `ano=2023`
  * `opcao=Processamento`
  * `subopcao=Viníferas`

---

### Detalhes dos parâmetros da rota /scrap/tabela

Esta rota realiza scraping dos dados do site da Embrapa Viticultura com base em três parâmetros obrigatórios:

### 🔹 ano (str)

Ano dos dados desejados.

- **Formato aceito:**  ano (ex: 2023)
- **Intervalo válido:** de **1970 a 2024**
- Valores fora desse intervalo serão rejeitados com erro 400.

---

### 🔹 opcao (str)

Corresponde às **abas principais** do site da Embrapa.

Você pode informar tanto o **nome descritivo** quanto o **código numérico** da aba.

| Nome              | Código (`opcao`) |
|-------------------|------------------|
| Produção          | `02`             |
| Processamento     | `03`             |
| Comercialização   | `04`             |
| Importação        | `05`             |
| Exportação        | `06`             |

---

### 🔹 subopcao (str)

Subcategorias específicas disponíveis apenas para algumas `opcao`.

Você pode informar tanto o **nome descritivo** quanto o **código numérico** da aba.

#### Para `Processamento (03)`

| Nome                          | Código |
|-------------------------------|--------|
| Viníferas                     | `01`   |
| Americanas e Híbridas         | `02`   |
| Uvas de Mesa                  | `03`   |
| Sem Classificação             | `04`   |

#### Para `Importação (05)`

| Nome            | Código |
|------------------|--------|
| Vinhos de Mesa   | `01`   |
| Espumantes       | `02`   |
| Uvas Frescas     | `03`   |
| Uvas Passas      | `04`   |
| Suco de Uva      | `05`   |

#### Para `Exportação (06)`

| Nome            | Código |
|------------------|--------|
| Vinhos de Mesa   | `01`   |
| Espumantes       | `02`   |
| Uvas Frescas     | `03`   |
| Suco de Uva      | `04`   |

---

### Observações

- Se a `opcao` for Produção (`02`) ou Comercialização (`04`), o valor da `subopcao` pode ser `"01"` ou omitido.
- Os parâmetros são **case-insensitive** e aceitam nomes com ou sem acento (ex: `"viniferas"`, `"Viníferas"`, `"viniferás"` → todos funcionam).
- Exemplo de chamada: `"/scrap/tabela?ano=2023&opcao=Processamento&subopcao=Viníferas"`

---

## Exemplo de uso com Postman

### 1. Criar usuário

- Método: `POST`
- URL: `http://localhost:8000/auth/usuario`
- Body → `raw` → `JSON`:
```json
{
  "usuario": "usuario1",
  "senha": "senha123",
  "email": "usuario1@email.com"
}
```

---

### 2. Obter token JWT

- Método: `POST`
- URL: `http://localhost:8000/auth/token`
- Authorization: tipo **Basic Auth**
  - Username: `usuario1`
  - Password: `senha123`

---

### 3. Acessar a rota protegida

- Método: `GET`
- URL: `http://localhost:8000/scrap/tabela?ano=2023&opcao=02&subopcao=01`
- Headers:
  - Key: `Authorization`
  - Value: `Bearer <seu_token_gerado>`

---

### Documentação interativa
A API possui documentação interativa acessível em `http://localhost:8000/docs` após iniciar o servidor.
Lá você pode testar as rotas, visualizar os schemas e exemplos facilmente.

---

## Licença

Distribuído sob a licença MIT.