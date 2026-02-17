"""NBalance — Outil de bilan azoté pour le palmier à huile."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import import_data, fields, parameters, simulations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup : créer les tables si elles n'existent pas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Outil de diagnostic et d'aide à la décision pour le calcul "
        "du bilan azoté sur le cycle complet du palmier à huile."
    ),
    lifespan=lifespan,
)

# CORS pour le frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrer les routers
app.include_router(import_data.router)
app.include_router(fields.router)
app.include_router(parameters.router)
app.include_router(simulations.router)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
