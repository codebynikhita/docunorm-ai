from fastapi import APIRouter

from app.api.v1.endpoints import auth, documents, ocr, portfolio, zugferd

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(ocr.router)
api_router.include_router(portfolio.router)
api_router.include_router(zugferd.router)
