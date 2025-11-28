from fastapi import APIRouter, Depends
from app.api.v1.schemas import DashboardData
from app.api.v1.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard(current_user = Depends(get_current_user)):
    """
    Получить общий dashboard с статистикой
    """
    # TODO: Получить реальные данные из БД
    return {
        "stats": {
            "total_predictions": 1250,
            "total_clients": 856,
            "avg_confidence": 0.87,
            "model_version": "1.0.0",
            "last_update": "2025-11-28T22:00:00Z",
            "metrics": [
                {"metric_name": "WMAE", "train_value": 0.1234, "test_value": 0.1456, "unit": ""},
                {"metric_name": "MAE", "train_value": 5234.50, "test_value": 6123.75, "unit": "₽"}
            ]
        },
        "income_distribution": [
            {"category": "LOW", "count": 320, "percentage": 37.4},
            {"category": "MIDDLE", "count": 380, "percentage": 44.4},
            {"category": "HIGH", "count": 156, "percentage": 18.2}
        ],
        "recent_predictions": [],
        "top_features": []
    }
