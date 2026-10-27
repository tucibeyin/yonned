from fastapi import APIRouter
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.persons import router as persons_router
from app.api.v1.endpoints.assets import router as assets_router
from app.api.v1.endpoints.vasifs import router as vasifs_router
from app.api.v1.endpoints.sessions import router as sessions_router
from app.api.v1.endpoints.processes import router as processes_router
from app.api.v1.endpoints.scanner import router as scanner_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(persons_router)
api_v1_router.include_router(assets_router)
api_v1_router.include_router(vasifs_router)
api_v1_router.include_router(sessions_router)
api_v1_router.include_router(processes_router)
api_v1_router.include_router(scanner_router)
