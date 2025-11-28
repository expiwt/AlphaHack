from fastapi import APIRouter, Depends, HTTPException
from app.api.v1.schemas import PredictionRequest, PredictionResponse
from app.api.v1.dependencies import get_current_user
from app.data.database import SessionLocal
from app.data.models import Client, Prediction, Recommendation, User
from sqlalchemy import desc
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/predictions/predict", response_model=PredictionResponse)
async def predict_income(
    request: PredictionRequest,
    current_user = Depends(get_current_user)
):
    """
    Получить прогноз дохода для клиента
    (На данный момент возвращает тестовые данные)
    """
    db = SessionLocal()
    try:
        # Получить клиента
        client = db.query(Client).filter_by(client_id=request.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Проверяем есть ли уже прогноз
        existing_pred = db.query(Prediction)\
            .filter_by(client_id=request.client_id)\
            .order_by(desc(Prediction.created_at))\
            .first()
        
        if existing_pred:
            return PredictionResponse(
                prediction_id=existing_pred.prediction_id,
                client_id=existing_pred.client_id,
                predicted_income=existing_pred.predicted_income,
                actual_income=client.income_real,
                confidence=existing_pred.confidence,
                income_category=existing_pred.category,
                error=abs(existing_pred.predicted_income - client.income_real),
                error_percent=abs(existing_pred.predicted_income - client.income_real) / client.income_real * 100,
                recommendations=[],
                explanation=[],
                timestamp="2025-11-28T22:00:00Z",
                model_version="1.0.0"
            )
        
        # Если прогноза нет, создаем тестовый
        predicted = client.income_real * 0.95  # Примерно 95% от реального
        confidence = 0.82
        category = "MIDDLE"
        
        # Сохраняем прогноз
        prediction = Prediction(
            prediction_id=str(uuid.uuid4()),
            client_id=request.client_id,
            predicted_income=predicted,
            confidence=confidence,
            category=category
        )
        db.add(prediction)
        db.commit()
        
        return PredictionResponse(
            prediction_id=prediction.prediction_id,
            client_id=request.client_id,
            predicted_income=predicted,
            actual_income=client.income_real,
            confidence=confidence,
            income_category=category,
            error=abs(predicted - client.income_real),
            error_percent=abs(predicted - client.income_real) / client.income_real * 100,
            recommendations=[],
            explanation=[],
            timestamp="2025-11-28T22:00:00Z",
            model_version="1.0.0"
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error predicting: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()
