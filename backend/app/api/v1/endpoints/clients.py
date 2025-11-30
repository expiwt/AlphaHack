from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Depends, BackgroundTasks
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
import pandas as pd
import xgboost as xgb
from scripts.load_clients import load_clients_from_csv

logger = logging.getLogger(__name__)
router = APIRouter()

def process_csv_with_ml(input_file_path: Path, output_file_path: Path) -> dict:
    """
    Обрабатывает CSV файл через ML модель напрямую, без subprocess
    
    Args:
        input_file_path: Путь к входному CSV
        output_file_path: Путь для сохранения результата
        
    Returns:
        dict с результатами обработки
    """
    try:
        logger.info(f"Начало обработки CSV: {input_file_path}")
        
        # Загружаем CSV в датафрейм
        df_test = pd.read_csv(input_file_path)
        logger.info(f"Загружено {len(df_test)} записей из CSV")
        
        # Проверяем обязательные поля
        required_columns = ['id', 'incomeValue']
        missing_columns = [col for col in required_columns if col not in df_test.columns]
        if missing_columns:
            raise ValueError(f"Отсутствуют обязательные колонки: {missing_columns}")
        
        # Убираем первые две колонки если они есть (обычно это индексы)
        if len(df_test.columns) > 2 and df_test.columns[0] == 'Unnamed: 0':
            df_test = df_test.iloc[:, 2:]
            logger.info("Удалены индексные колонки")
        
        # Загружаем модель
        model_path = Path(__file__).parent.parent.parent / "model.json"
        if not model_path.exists():
            raise FileNotFoundError(f"Модель не найдена: {model_path}")
        
        logger.info("Загрузка ML модели...")
        loaded_model = xgb.Booster()
        loaded_model.load_model(str(model_path))
        
        # Подготовка признаков для теста (без 'target' и 'w' если они есть)
        features_to_drop = ["target", "w"]
        X_test = df_test.drop(columns=[col for col in features_to_drop if col in df_test.columns])
        
        # Логируем используемые признаки
        logger.info(f"Используется {len(X_test.columns)} признаков для предсказания")
        
        # Создание DMatrix для теста
        dtest = xgb.DMatrix(X_test)
        
        # Получение предсказаний
        logger.info("Выполнение предсказаний...")
        predictions = loaded_model.predict(dtest)
        logger.info(f"Получено {len(predictions)} предсказаний")
        
        # Вычисляем hdb_income_ratio если есть необходимые поля
        if 'hdb_outstand_sum' in df_test.columns and 'incomeValue' in df_test.columns:
            df_test['hdb_income_ratio'] = df_test['hdb_outstand_sum'] / df_test['incomeValue']
            logger.info("Вычислен hdb_income_ratio")
        elif 'hdb_income_ratio' not in df_test.columns:
            # Если поля нет, создаем пустую колонку
            df_test['hdb_income_ratio'] = None
            logger.info("hdb_income_ratio не найден, создана пустая колонка")
        
        # Вычисляем PDN (Показатель долговой нагрузки)
        if 'hdb_outstand_sum' in df_test.columns and 'incomeValue' in df_test.columns:
            df_test['PDN'] = (df_test['hdb_outstand_sum'] / df_test['incomeValue']) * 100
            logger.info("Вычислен PDN")
        else:
            df_test['PDN'] = None
            logger.info("Не удалось вычислить PDN, создана пустая колонка")
        
        # Создание результирующего DataFrame с нужными полями
        pred_df = pd.DataFrame({
            "id": df_test['id'].astype(str),
            "target": predictions,  # Предсказанный доход
            "incomeValue": df_test['incomeValue'],
            "avg_cur_cr_turn": df_test.get('avg_cur_cr_turn', None),
            "ovrd_sum": df_test.get('ovrd_sum', 0.0),
            "loan_cur_amt": df_test.get('loan_cur_amt', 0.0),
            "hdb_income_ratio": df_test.get('hdb_income_ratio', None),
            "PDN": df_test.get('PDN', None)
        })
        
        # Заполняем NaN значения
        pred_df['ovrd_sum'] = pred_df['ovrd_sum'].fillna(0.0)
        pred_df['loan_cur_amt'] = pred_df['loan_cur_amt'].fillna(0.0)
        
        # Сохраняем результат
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        pred_df.to_csv(output_file_path, index=False)
        logger.info(f"Файл обработан и сохранен: {output_file_path}")
        
        return {
            "processed_records": len(pred_df),
            "columns_used": list(X_test.columns),
            "prediction_stats": {
                "min": float(predictions.min()),
                "max": float(predictions.max()),
                "mean": float(predictions.mean())
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка обработки CSV: {e}")
        raise

@router.post("/clients/upload-csv")
async def upload_clients_csv(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """
    Загружает CSV файл, обрабатывает через ML модель и загружает в БД.
    
    Процесс:
    1. Сохраняет загруженный файл
    2. Обрабатывает через ML модель напрямую
    3. Загружает результат в БД
    """
    # Проверяем формат файла
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Файл должен быть в формате CSV")
    
    # Создаем директорию для временных файлов
    temp_dir = Path(__file__).parent.parent.parent / "data" / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    input_file_path = temp_dir / f"input_{uuid.uuid4().hex[:8]}.csv"
    output_file_path = Path(__file__).parent.parent.parent / "data" / "fin_clients.csv"
    
    db = SessionLocal()
    
    try:
        # Сохраняем загруженный файл
        with open(input_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Файл сохранен: {input_file_path}")
        
        # Обрабатываем CSV через ML модель
        ml_result = process_csv_with_ml(input_file_path, output_file_path)
        
        # Загружаем данные в БД в транзакции
        db.begin()
        try:
            # Удаляем все существующие клиенты
            deleted_count = db.query(Client).delete()
            logger.info(f"Удалено существующих клиентов: {deleted_count}")
            
            # Загружаем новых клиентов
            load_result = load_clients_from_csv(str(output_file_path))
            
            db.commit()
            
            return {
                "message": "Файл успешно обработан и загружен",
                "uploaded_file": file.filename,
                "processed_clients": load_result['loaded'],
                "total_records": load_result['total'],
                "errors": load_result['errors'],
                "ml_processing": ml_result,
                "output_file": str(output_file_path)
            }
            
        except Exception as db_error:
            db.rollback()
            logger.error(f"Ошибка транзакции БД: {db_error}")
            raise HTTPException(
                status_code=500, 
                detail=f"Ошибка загрузки в БД: {str(db_error)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка загрузки CSV: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки: {str(e)}")
    finally:
        db.close()
        # Удаляем временный файл
        if input_file_path.exists():
            try:
                input_file_path.unlink()
                logger.info(f"Временный файл удален: {input_file_path}")
            except Exception as e:
                logger.warning(f"Не удалось удалить временный файл: {e}")

# Остальной код эндпоинтов остается без изменений...
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
            "PDN": client.PDN,  # Новое поле
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
        elif sort == "PDN":
            query = query.order_by(desc(Client.PDN) if order == "desc" else Client.PDN)
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
                "PDN": client.PDN,  # Новое поле
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
