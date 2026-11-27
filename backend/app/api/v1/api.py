from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    benchmark,
    cache,
    collision,
    documents,
    dora_register,
    horizon,
    metrics,
    negotiation_sim,
    ocr,
    portfolio,
    rerank,
    tenants,
    zugferd,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(benchmark.router, prefix="/benchmark", tags=["Hardening Benchmark"])
api_router.include_router(cache.router)
api_router.include_router(collision.router)
api_router.include_router(documents.router)
api_router.include_router(dora_register.router)
api_router.include_router(horizon.router)
api_router.include_router(metrics.router, prefix="/metrics", tags=["Metrics & Observability"])
api_router.include_router(negotiation_sim.router)
api_router.include_router(ocr.router)
api_router.include_router(portfolio.router)
api_router.include_router(rerank.router)
api_router.include_router(tenants.router)
api_router.include_router(zugferd.router)
