from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.scrap.routes import router as scrap_router
from app.database import engine
from app.models import Base

app = FastAPI(title="Tech Challenge API", version="1.0.0")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(scrap_router)