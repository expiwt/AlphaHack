"""
Загружает клиентов из CSV в БД.

CSV формат:
  id, target, incomeValue, avg_cur_cr_turn, ovrd_sum, loan_cur_amt, hdb_income_ratio, PDN

Скрипт:
1. Читает fin_clients.csv (результат ML обработки)
2. Парсит поля с валидацией
3. INSERT в таблицу clients с обработкой дубликатов
"""

import csv
import os
import sys
from pathlib import Path

# Добавляем путь к корню проекта
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, exc
from app.data.database import SessionLocal, engine
from app.data.models import Client
import logging

logger = logging.getLogger(__name__)

def safe_float(value, default=0.0):
    """Безопасное преобразование в float"""
    if value is None or value == '':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_str(value):
    """Безопасное преобразование в строку"""
    if value is None:
        return ""
    return str(value).strip()

def load_clients_from_csv(csv_path: str = None) -> dict:
    """
    Загружает клиентов из CSV файла в БД.
    
    Args:
        csv_path: Путь к CSV файлу. Если None, ищет backend/data/fin_clients.csv
    
    Returns:
        dict с результатами: {
            'total': общее количество записей,
            'loaded': успешно загружено,
            'errors': количество ошибок,
            'errors_list': список ошибок
        }
    """
    if csv_path is None:
        # Ищем CSV в backend/data/fin_clients.csv (результат ML обработки)
        script_dir = Path(__file__).parent
        csv_path = script_dir.parent / "data" / "fin_clients.csv"
    
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        logger.error(f"CSV файл не найден: {csv_path}")
        return {'total': 0, 'loaded': 0, 'errors': 0, 'errors_list': ['CSV файл не найден']}
    
    db = SessionLocal()
    loaded_count = 0
    error_count = 0
    errors_list = []
    total_rows = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            total_rows = sum(1 for _ in reader)  # Считаем общее количество строк
            f.seek(0)  # Возвращаемся в начало файла
            next(reader)  # Пропускаем заголовок
            
            batch_size = 100
            batch = []
            
            for row_num, row in enumerate(reader, start=2):  # Начинаем с 2 (заголовок - строка 1)
                try:
                    # Валидация и парсинг данных
                    client_id = safe_str(row.get('id'))
                    if not client_id:
                        raise ValueError("ID клиента не может быть пустым")
                    
                    # Парсим числовые поля
                    target = safe_float(row.get('target'), None)
                    incomeValue = safe_float(row.get('incomeValue'), None)
                    avg_cur_cr_turn = safe_float(row.get('avg_cur_cr_turn'), None)
                    ovrd_sum = safe_float(row.get('ovrd_sum'), 0.0)
                    loan_cur_amt = safe_float(row.get('loan_cur_amt'), 0.0)
                    hdb_income_ratio = safe_float(row.get('hdb_income_ratio'), None)
                    PDN = safe_float(row.get('PDN'), None)  # Новое поле
                    
                    # Создаем клиента
                    client = Client(
                        id=client_id,
                        target=target,
                        incomeValue=incomeValue,
                        avg_cur_cr_turn=avg_cur_cr_turn,
                        ovrd_sum=ovrd_sum,
                        loan_cur_amt=loan_cur_amt,
                        hdb_income_ratio=hdb_income_ratio,
                        PDN=PDN  # Новое поле
                    )
                    
                    batch.append(client)
                    
                    # Пакетная вставка
                    if len(batch) >= batch_size:
                        db.bulk_save_objects(batch)
                        db.commit()
                        loaded_count += len(batch)
                        batch = []
                        logger.debug(f"Загружено {loaded_count} клиентов...")
                    
                except Exception as e:
                    error_count += 1
                    error_msg = f"Строка {row_num}: {str(e)}"
                    errors_list.append(error_msg)
                    logger.warning(error_msg)
                    continue
            
            # Обрабатываем оставшийся пакет
            if batch:
                db.bulk_save_objects(batch)
                db.commit()
                loaded_count += len(batch)
        
        logger.info(f"✓ Загружено {loaded_count} клиентов из {total_rows} записей")
        if error_count > 0:
            logger.warning(f"⚠ Пропущено {error_count} записей из-за ошибок")
        
        return {
            'total': total_rows,
            'loaded': loaded_count,
            'errors': error_count,
            'errors_list': errors_list
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Ошибка загрузки CSV: {e}", exc_info=True)
        return {
            'total': total_rows,
            'loaded': loaded_count,
            'errors': error_count + 1,
            'errors_list': errors_list + [f"Общая ошибка: {str(e)}"]
        }
    finally:
        db.close()

if __name__ == "__main__":
    # Запуск скрипта напрямую
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    result = load_clients_from_csv()
    print(f"Результат загрузки: {result['loaded']} из {result['total']} записей")
    if result['errors'] > 0:
        print(f"Ошибки: {result['errors']}")
        for error in result['errors_list'][:5]:  # Показываем первые 5 ошибок
            print(f"  - {error}")
