"""
Analytics routers initialization - Phase 3
"""
from app.api.routers.analytics.metrics import router as metrics_router
from app.api.routers.analytics.tactics import router as tactics_router
from app.api.routers.analytics.xt import router as xt_router
from app.api.routers.analytics.events import router as events_router

__all__ = [
    "metrics_router",
    "tactics_router",
    "xt_router",
    "events_router"
]
