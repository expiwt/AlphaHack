"""
Загружает клиентов из CSV в БД.

CSV формат:
  id, target, incomeValue, avg_cur_cr_turn, ovrd_sum, loan_cur_amt, hdb_income_ratio

Скрипт:
1. Читает fin_clients.csv (результат ML обработки)
2. Парсит поля
3. INSERT в таблицу clients
"""

import csv
import os
import sys
from pathlib import Path

# Добавляем путь к корню проекта
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.data.database import SessionLocal, engine
from app.data.models import Client
import logging

logger = logging.getLogger(__name__)

def load_clients_from_csv(csv_path: str = None) -> int:
    """
    Загружает клиентов из CSV файла в БД.
    
    Args:
        csv_path: Путь к CSV файлу. Если None, ищет backend/data/fin_clients.csv
    
    Returns:
        Количество загруженных клиентов
    """
    if csv_path is None:
        # Ищем CSV в backend/data/fin_clients.csv (результат ML обработки)
        script_dir = Path(__file__).parent
        csv_path = script_dir.parent / "data" / "fin_clients.csv"
    
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        logger.warning(f"CSV файл не найден: {csv_path}")
        return 0
    
    db = SessionLocal()
    loaded_count = 0
    
    try:
        # Всегда загружаем данные из файла (старые данные уже удалены в endpoint)
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    # Парсим данные из CSV
                    client_id = str(row['id']).strip()
                    target = float(row['target']) if row.get('target') and row['target'].strip() else None
                    incomeValue = float(row['incomeValue']) if row.get('incomeValue') and row['incomeValue'].strip() else None
                    avg_cur_cr_turn = float(row['avg_cur_cr_turn']) if row.get('avg_cur_cr_turn') and row['avg_cur_cr_turn'].strip() else None
                    ovrd_sum = float(row['ovrd_sum']) if row.get('ovrd_sum') and row['ovrd_sum'].strip() else 0.0
                    loan_cur_amt = float(row['loan_cur_amt']) if row.get('loan_cur_amt') and row['loan_cur_amt'].strip() else 0.0
                    hdb_income_ratio = float(row['hdb_income_ratio']) if row.get('hdb_income_ratio') and row['hdb_income_ratio'].strip() else None
                    
                    # Создаем клиента
                    client = Client(
                        id=client_id,
                        target=target,
                        incomeValue=incomeValue,
                        avg_cur_cr_turn=avg_cur_cr_turn,
                        ovrd_sum=ovrd_sum,
                        loan_cur_amt=loan_cur_amt,
                        hdb_income_ratio=hdb_income_ratio
                    )
                    
                    db.add(client)
                    loaded_count += 1
                    
                except Exception as e:
                    logger.error(f"Ошибка при обработке строки {row}: {e}")
                    continue
        
        db.commit()
        logger.info(f"✓ Загружено {loaded_count} клиентов из CSV")
        return loaded_count
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Ошибка загрузки CSV: {e}", exc_info=True)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # Запуск скрипта напрямую
    logging.basicConfig(level=logging.INFO)
    count = load_clients_from_csv()
    print(f"Загружено клиентов: {count}")
