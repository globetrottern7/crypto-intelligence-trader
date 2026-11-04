from hmac import compare_digest

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.health import router as health_router
from app.api.routes.intelligence import router as intelligence_router
from app.api.routes.market_data import router as market_data_router
from app.api.routes.paper import router as paper_router
from app.api.routes.system import router as system_router
from app.core.config import settings

app = FastAPI(
    title="Crypto Intelligence & Trading Assistant API",
    version="0.3.0",
    description="Research, quantitative analysis and paper trading only. No live exchange execution.",
)
app.add_middleware(
    CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=False,
    allow_methods=["GET", "POST"], allow_headers=["Content-Type", "Authorization"],
)


@app.middleware("http")
async def protect_private_api(request: Request, call_next):
    if settings.app_env.lower() == "production" and request.url.path.startswith("/api/v1/"):
        if not settings.api_access_token:
            return JSONResponse(status_code=503, content={"detail": "API_ACCESS_TOKEN is not configured."})
        supplied = request.headers.get("authorization", "")
        if not compare_digest(supplied, f"Bearer {settings.api_access_token}"):
            return JSONResponse(status_code=401, content={"detail": "Unauthorised"})
    return await call_next(request)


app.include_router(health_router)
app.include_router(system_router, prefix="/api/v1")
app.include_router(market_data_router, prefix="/api/v1")
app.include_router(intelligence_router, prefix="/api/v1")
app.include_router(paper_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"name": "Crypto Intelligence & Trading Assistant", "status": "running", "mode": "paper_only"}
