from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Depends
from app.data.database import SessionLocal
from app.data.models import Client, Prediction
from app.services.credit_service import calculate_credit_decision
from app.api.v1.dependencies import get_current_user
from sqlalchemy import desc, or_
import uuid
import logging
import os
import subprocess
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/clients/upload-csv")
async def upload_clients_csv(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """
    Загружает CSV файл, обрабатывает через ML скрипт и загружает в БД.
    
    Процесс:
    1. Сохраняет загруженный файл
    2. Запускает ml_script_clients.py для обработки
    3. Загружает результат из fin_clients.csv в БД
    """
    # Проверяем формат файла
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Файл должен быть в формате CSV")
    
    # Создаем директорию для временных файлов
    temp_dir = Path(__file__).parent.parent.parent / "data" / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    input_file_path = temp_dir / f"input_{uuid.uuid4().hex[:8]}.csv"
    output_file_path = Path(__file__).parent.parent.parent / "data" / "fin_clients.csv"
    ml_script_path = Path(__file__).parent.parent.parent / "ml_script_clients.py"
    
    try:
        # Сохраняем загруженный файл
        with open(input_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Файл сохранен: {input_file_path}")
        
        # Запускаем ML скрипт
        try:
            result = subprocess.run(
                ["python", str(ml_script_path), str(input_file_path), str(output_file_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 минут таймаут
            )
            
            if result.returncode != 0:
                logger.error(f"Ошибка ML скрипта: {result.stderr}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Ошибка обработки файла: {result.stderr}"
                )
            
            logger.info(f"ML скрипт выполнен успешно: {result.stdout}")
            
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=500, detail="Превышено время ожидания обработки файла")
        except Exception as e:
            logger.error(f"Ошибка запуска ML скрипта: {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка запуска ML скрипта: {str(e)}")
        
        # Проверяем наличие выходного файла
        if not output_file_path.exists():
            raise HTTPException(status_code=500, detail="Выходной файл не был создан")
        
        # Загружаем данные из fin_clients.csv в БД
        db = SessionLocal()
        try:
            # Удаляем все существующие клиенты
            db.query(Client).delete()
            db.commit()
            logger.info("Существующие клиенты удалены")
            
            # Загружаем новых клиентов
            from scripts.load_clients import load_clients_from_csv
            count = load_clients_from_csv(str(output_file_path))
            
            return {
                "message": "Файл успешно обработан и загружен",
                "uploaded_file": file.filename,
                "processed_clients": count,
                "output_file": str(output_file_path)
            }
        finally:
            db.close()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка загрузки CSV: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки: {str(e)}")
    finally:
        # Удаляем временный файл
        if input_file_path.exists():
            try:
                input_file_path.unlink()
            except:
                pass

@router.get("/clients/{client_id}")
async def get_client(client_id: str):
    """Получить клиента"""
    db = SessionLocal()
    try:
        client = db.query(Client).filter_by(id=client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Not found")
        
        result = {
            "id": client.id,
            "target": client.target,
            "incomeValue": client.incomeValue,
            "avg_cur_cr_turn": client.avg_cur_cr_turn,
            "ovrd_sum": client.ovrd_sum,
            "loan_cur_amt": client.loan_cur_amt,
            "hdb_income_ratio": client.hdb_income_ratio,
        }
        
        # Вычисляем решение по кредиту на основе новых полей
        if client.incomeValue and client.ovrd_sum is not None:
            # Рассчитываем долговую нагрузку: просрочка / доход
            debt_burden_ratio = (client.ovrd_sum / client.incomeValue) if client.incomeValue > 0 else 0.0
            
            credit_decision = calculate_credit_decision({
                "debt_burden_ratio": debt_burden_ratio,
                "predicted_income": client.incomeValue or 0.0,
                "total_debt": client.ovrd_sum or 0.0,
                "loan_amount": client.loan_cur_amt or 0.0,
                "avg_cur_cr_turn": client.avg_cur_cr_turn or 0.0
            })
            result.update({
                "risk_level": credit_decision["risk_level"],
                "recommendation": credit_decision["recommendation"],
                "reasoning": credit_decision["reasoning"]
            })
        
        return result
    finally:
        db.close()

@router.get("/clients")
async def list_clients(
    sort: str = Query("incomeValue", description="Поле для сортировки"),
    order: str = Query("desc", description="Порядок сортировки (asc/desc)"),
    limit: int = Query(50, description="Лимит записей"),
    offset: int = Query(0, description="Смещение"),
    risk_level: str = Query(None, description="Фильтр по уровню риска (LOW/MEDIUM/HIGH)")
):
    """Получить список клиентов с фильтрами"""
    db = SessionLocal()
    try:
        query = db.query(Client)
        
        # Сортировка
        if sort == "incomeValue":
            query = query.order_by(desc(Client.incomeValue) if order == "desc" else Client.incomeValue)
        elif sort == "target":
            query = query.order_by(desc(Client.target) if order == "desc" else Client.target)
        elif sort == "ovrd_sum":
            query = query.order_by(desc(Client.ovrd_sum) if order == "desc" else Client.ovrd_sum)
        elif sort == "loan_cur_amt":
            query = query.order_by(desc(Client.loan_cur_amt) if order == "desc" else Client.loan_cur_amt)
        elif sort == "hdb_income_ratio":
            query = query.order_by(desc(Client.hdb_income_ratio) if order == "desc" else Client.hdb_income_ratio)
        else:
            query = query.order_by(desc(Client.incomeValue) if order == "desc" else Client.incomeValue)
        
        total = query.count()
        clients = query.offset(offset).limit(limit).all()
        
        items = []
        for client in clients:
            item = {
                "id": client.id,
                "target": client.target,
                "incomeValue": client.incomeValue,
                "avg_cur_cr_turn": client.avg_cur_cr_turn,
                "ovrd_sum": client.ovrd_sum,
                "loan_cur_amt": client.loan_cur_amt,
                "hdb_income_ratio": client.hdb_income_ratio,
            }
            
            # Вычисляем решение по кредиту
            if client.incomeValue and client.ovrd_sum is not None:
                debt_burden_ratio = (client.ovrd_sum / client.incomeValue) if client.incomeValue > 0 else 0.0
                
                credit_decision = calculate_credit_decision({
                    "debt_burden_ratio": debt_burden_ratio,
                    "predicted_income": client.incomeValue or 0.0,
                    "total_debt": client.ovrd_sum or 0.0,
                    "loan_amount": client.loan_cur_amt or 0.0,
                    "avg_cur_cr_turn": client.avg_cur_cr_turn or 0.0
                })
                item.update({
                    "risk_level": credit_decision["risk_level"],
                    "recommendation": credit_decision["recommendation"],
                    "reasoning": credit_decision["reasoning"]
                })
                
                # Фильтр по risk_level (если указан)
                if risk_level and credit_decision["risk_level"] != risk_level:
                    continue
            
            items.append(item)
        
        return {"total": total, "items": items}
    finally:
        db.close()
