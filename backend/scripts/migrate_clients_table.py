"""
Скрипт миграции: обновление структуры таблицы clients
Добавляет все необходимые колонки если их нет
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

def migrate_clients_table():
    """Обновляет структуру таблицы clients, добавляя недостающие колонки"""
    try:
        with engine.begin() as conn:
            # Список всех необходимых колонок (incomeValue с кавычками)
            required_columns = {
                'id': 'VARCHAR(50)',
                'target': 'FLOAT',
                '"incomeValue"': 'FLOAT',  # С кавычками для сохранения camelCase
                'avg_cur_cr_turn': 'FLOAT',
                'ovrd_sum': 'FLOAT DEFAULT 0',
                'loan_cur_amt': 'FLOAT DEFAULT 0',
                'hdb_income_ratio': 'FLOAT',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            }
            
            # Проверяем существующие колонки
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'clients'
            """))
            existing_columns = {row[0]: row for row in result.fetchall()}
            existing_columns_lower = {col.lower(): col for col in existing_columns.keys()}
            
            logger.info(f"Существующие колонки: {list(existing_columns.keys())}")
            
            # Переименовываем client_id в id если нужно
            if 'client_id' in existing_columns and 'id' not in existing_columns:
                logger.info("Переименовываем client_id в id...")
                conn.execute(text("ALTER TABLE clients RENAME COLUMN client_id TO id"))
                logger.info("✓ client_id переименован в id")
                # Обновляем список существующих колонок
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'clients'
                """))
                existing_columns = {row[0]: row for row in result.fetchall()}
                existing_columns_lower = {col.lower(): col for col in existing_columns.keys()}
            
            # Переименовываем incomevalue в "incomeValue" если нужно
            if 'incomevalue' in existing_columns_lower and 'incomeValue' not in existing_columns:
                logger.info("Переименовываем incomevalue в incomeValue...")
                conn.execute(text('ALTER TABLE clients RENAME COLUMN incomevalue TO "incomeValue"'))
                logger.info("✓ incomevalue переименован в incomeValue")
                # Обновляем список существующих колонок
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'clients'
                """))
                existing_columns = {row[0]: row for row in result.fetchall()}
                existing_columns_lower = {col.lower(): col for col in existing_columns.keys()}
            
            # Добавляем недостающие колонки
            for col_name, col_def in required_columns.items():
                # Проверяем существование колонки (учитываем регистр)
                col_name_check = col_name.strip('"').lower()
                if col_name_check not in existing_columns_lower and col_name not in existing_columns:
                    logger.info(f"Добавляем колонку {col_name}...")
                    try:
                        conn.execute(text(f"ALTER TABLE clients ADD COLUMN {col_name} {col_def}"))
                        logger.info(f"✓ Колонка {col_name} добавлена")
                        
                        # Если это id и нет первичного ключа, пытаемся добавить
                        if col_name == 'id':
                            try:
                                # Проверяем есть ли уже PK
                                pk_result = conn.execute(text("""
                                    SELECT constraint_name 
                                    FROM information_schema.table_constraints 
                                    WHERE table_name = 'clients' AND constraint_type = 'PRIMARY KEY'
                                """))
                                if not pk_result.fetchone():
                                    conn.execute(text("ALTER TABLE clients ADD PRIMARY KEY (id)"))
                                    logger.info("✓ Primary key добавлен для id")
                            except Exception as pk_e:
                                logger.warning(f"Не удалось добавить PRIMARY KEY для id: {pk_e}")
                    except Exception as e:
                        logger.warning(f"Не удалось добавить колонку {col_name}: {e}")
            
            # Удаляем неиспользуемые колонки
            columns_to_drop = ['adminarea', 'city_smart_name']
            for col_name in columns_to_drop:
                if col_name in existing_columns:
                    logger.info(f"Удаляем колонку {col_name}...")
                    conn.execute(text(f"ALTER TABLE clients DROP COLUMN IF EXISTS {col_name}"))
                    logger.info(f"✓ Колонка {col_name} удалена")
            
            # Проверяем финальную структуру
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'clients'
                ORDER BY ordinal_position
            """))
            final_columns = result.fetchall()
            logger.info("=" * 50)
            logger.info("Финальная структура таблицы clients:")
            for col in final_columns:
                logger.info(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
            logger.info("=" * 50)
            
    except Exception as e:
        logger.error(f"Ошибка миграции: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    migrate_clients_table()

