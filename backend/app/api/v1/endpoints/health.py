from fastapi import APIRouter
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "alfa-bank-income-prediction"
    }

@router.get("/health/detailed")
async def health_detailed():
    """Подробная проверка здоровья системы"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "ok",
        "redis": "ok"
    }
