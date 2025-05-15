from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.scrap.routes import router as scrap_router
from app.database import engine
from app.models import Base

app = FastAPI(title="Tech Challenge API", 
              description=(
              "API que realiza scraping dos dados da Embrapa Viticultura. "
            "Utiliza autenticação JWT e aplica fallback com dados armazenados em "
            "banco caso o scraping falhe."
            ),
              version="1.0.0",
              contact={
                  "name": "Celso Gabriel Vieira Ribeiro Lopes",
                  "email": "c.gabriel.vieira@hotmail.com",
                  "url": "https://github.com/seu-usuario/seu-repo"
              })

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(scrap_router)