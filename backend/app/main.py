from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_v1_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Başlangıç (Startup) işlemleri
    print(f"🚀 {settings.PROJECT_NAME} başlatılıyor... Ortam: {settings.ENVIRONMENT}")
    yield
    # Kapanış (Shutdown) işlemleri
    print(f"🛑 {settings.PROJECT_NAME} kapatılıyor...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Yonned Universal Asset & Process Management Platform API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# CORS Middleware (Mobil uygulama ve Müşteri Tracker için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 Router Bağlantısı
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    """Sistem sağlık kontrolü ve sürüm bilgisi."""
    return {
        "status": "healthy",
        "service": "yonned-api",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
