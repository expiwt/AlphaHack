"""
Скрипт миграции: переименование client_id в id в таблице clients
"""
import sys
from pathlib import Path

# Добавляем путь к корню проекта
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.data.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_client_id_to_id():
    """Переименовывает колонку client_id в id если она существует"""
    try:
        # Проверяем существует ли колонка client_id
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'clients' AND column_name = 'client_id'
            """))
            
            if result.fetchone():
                logger.info("Найдена колонка client_id, переименовываем в id...")
                with engine.begin() as trans_conn:
                    trans_conn.execute(text("ALTER TABLE clients RENAME COLUMN client_id TO id"))
                logger.info("✓ Колонка переименована: client_id -> id")
            else:
                logger.info("Колонка client_id не найдена, проверяем наличие id...")
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'clients' AND column_name = 'id'
                """))
                if result.fetchone():
                    logger.info("✓ Колонка id уже существует")
                else:
                    logger.warning("⚠ Колонка id не найдена в таблице clients")
            
            # Проверяем структуру таблицы
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'clients'
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()
            logger.info(f"Структура таблицы clients: {[c[0] for c in columns]}")
            
    except Exception as e:
        logger.error(f"Ошибка миграции: {e}")
        raise

if __name__ == "__main__":
    migrate_client_id_to_id()

