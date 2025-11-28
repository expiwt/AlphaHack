from fastapi import APIRouter, HTTPException, Query
from app.data.database import SessionLocal
from app.data.models import Client, Prediction
from sqlalchemy import desc
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/clients/seed/data")
async def seed_test_data():
    """Создать тестовые данные"""
    db = SessionLocal()
    try:
        # Проверяем есть ли уже данные
        count = db.query(Client).count()
        if count > 0:
            return {"message": "Data already exists", "count": count}
        
        # Создаем клиентов вручную (НЕ через **data)
        c1 = Client(
            client_id="cli_test_001",
            age=35,
            gender="M",
            city="Moscow",
            region="Moscow",
            income_real=150000
        )
        c2 = Client(
            client_id="cli_test_002",
            age=28,
            gender="F",
            city="SPB",
            region="Leningrad",
            income_real=85000
        )
        c3 = Client(
            client_id="cli_test_003",
            age=42,
            gender="M",
            city="Moscow",
            region="Moscow",
            income_real=250000
        )
        c4 = Client(
            client_id="cli_test_004",
            age=31,
            gender="F",
            city="Ekaterinburg",
            region="Sverdlovsk",
            income_real=95000
        )
        c5 = Client(
            client_id="cli_test_005",
            age=55,
            gender="M",
            city="Moscow",
            region="Moscow",
            income_real=350000
        )
        
        db.add(c1)
        db.add(c2)
        db.add(c3)
        db.add(c4)
        db.add(c5)
        db.commit()
        
        # Создаем прогнозы
        for client in [c1, c2, c3, c4, c5]:
            pred = Prediction(
                prediction_id=str(uuid.uuid4()),
                client_id=client.client_id,
                predicted_income=round(client.income_real * 0.95, 2),
                confidence=0.82,
                category="MIDDLE"
            )
            db.add(pred)
        
        db.commit()
        
        logger.info("✓ Test data created successfully")
        return {
            "message": "✓ Test data created",
            "created_clients": 5,
            "clients": ["cli_test_001", "cli_test_002", "cli_test_003", "cli_test_004", "cli_test_005"]
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Seed error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        db.close()

@router.get("/clients/{client_id}")
async def get_client(client_id: str):
    """Получить клиента"""
    db = SessionLocal()
    try:
        client = db.query(Client).filter_by(client_id=client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Not found")
        
        result = {
            "client_id": client.client_id,
            "age": client.age,
            "gender": client.gender,
            "city": client.city,
            "region": client.region,
            "income_real": client.income_real,
        }
        
        pred = db.query(Prediction).filter_by(client_id=client_id).order_by(desc(Prediction.created_at)).first()
        if pred:
            result.update({
                "income_predicted": pred.predicted_income,
                "confidence": pred.confidence,
                "income_category": pred.category
            })
        
        return result
    finally:
        db.close()

@router.get("/clients")
async def list_clients(
    sort: str = Query("income_real"),
    order: str = Query("desc"),
    limit: int = Query(50),
    offset: int = Query(0)
):
    """Получить список клиентов"""
    db = SessionLocal()
    try:
        query = db.query(Client)
        
        if sort == "age":
            query = query.order_by(desc(Client.age) if order == "desc" else Client.age)
        else:
            query = query.order_by(desc(Client.income_real) if order == "desc" else Client.income_real)
        
        total = query.count()
        clients = query.offset(offset).limit(limit).all()
        
        items = []
        for client in clients:
            item = {
                "client_id": client.client_id,
                "age": client.age,
                "gender": client.gender,
                "city": client.city,
                "region": client.region,
                "income_real": client.income_real,
            }
            
            pred = db.query(Prediction).filter_by(client_id=client.client_id).order_by(desc(Prediction.created_at)).first()
            if pred:
                item.update({
                    "income_predicted": pred.predicted_income,
                    "confidence": pred.confidence,
                    "income_category": pred.category
                })
            
            items.append(item)
        
        return {"total": total, "items": items}
    finally:
        db.close()
