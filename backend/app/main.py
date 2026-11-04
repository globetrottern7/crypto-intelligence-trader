from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.market_data import router as market_data_router
from app.api.routes.system import router as system_router
from app.core.config import settings

app = FastAPI(
    title="Crypto Intelligence & Trading Assistant API",
    version="0.2.0",
    description="Market-data foundation. Live order execution is intentionally unavailable.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)
app.include_router(health_router)
app.include_router(system_router, prefix="/api/v1")
app.include_router(market_data_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"name": "Crypto Intelligence & Trading Assistant", "status": "running"}
