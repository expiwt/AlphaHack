from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.data.models import Base
import logging

logger = logging.getLogger(__name__)

# Engine creation
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Проверка соединения перед использованием
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session() -> Session:
    """Dependency для получения БД сессии"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Инициализация БД (создание таблиц)"""
    try:
        logger.info("Initializing database...")
        
        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)
        
        logger.info("✓ Database tables created/verified")
        
        # Миграция таблицы clients: добавляем недостающие колонки
        with engine.begin() as conn:
            # Список необходимых колонок (incomeValue с кавычками для сохранения регистра)
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
            
            # Проверяем существующие колонки (учитываем регистр)
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'clients'
            """))
            existing_columns = {row[0] for row in result.fetchall()}
            existing_columns_lower = {col.lower(): col for col in existing_columns}
            
            logger.info(f"Существующие колонки в clients: {existing_columns}")
            
            # Переименовываем client_id в id если нужно
            if 'client_id' in existing_columns and 'id' not in existing_columns:
                logger.info("Migrating: renaming client_id to id...")
                conn.execute(text("ALTER TABLE clients RENAME COLUMN client_id TO id"))
                logger.info("✓ Migration completed: client_id -> id")
                existing_columns.remove('client_id')
                existing_columns.add('id')
                # Обновляем словарь для проверки в нижнем регистре
                existing_columns_lower = {col.lower(): col for col in existing_columns}
            
            # Переименовываем incomevalue в "incomeValue" если нужно
            incomevalue_original = existing_columns_lower.get('incomevalue')
            if incomevalue_original and 'incomeValue' not in existing_columns:
                logger.info(f"Migrating: renaming {incomevalue_original} to incomeValue...")
                conn.execute(text(f'ALTER TABLE clients RENAME COLUMN "{incomevalue_original}" TO "incomeValue"'))
                logger.info("✓ Migration completed: incomevalue -> incomeValue")
                # Обновляем множества после переименования
                existing_columns.discard(incomevalue_original)  # Используем discard вместо remove
                existing_columns.add('incomeValue')
                # Обновляем словарь для проверки в нижнем регистре
                existing_columns_lower = {col.lower(): col for col in existing_columns}
            
            # Добавляем недостающие колонки
            for col_name, col_def in required_columns.items():
                # Проверяем как в нижнем регистре, так и с кавычками
                col_name_check = col_name.strip('"').lower()
                if col_name_check not in existing_columns_lower and col_name not in existing_columns:
                    logger.info(f"Adding column {col_name}...")
                    try:
                        conn.execute(text(f"ALTER TABLE clients ADD COLUMN {col_name} {col_def}"))
                        logger.info(f"✓ Column {col_name} added")
                    except Exception as e:
                        logger.warning(f"Could not add column {col_name}: {e}")
            
            # Удаляем неиспользуемые колонки
            columns_to_drop = ['adminarea', 'city_smart_name']
            for col_name in columns_to_drop:
                if col_name in existing_columns:
                    logger.info(f"Dropping column {col_name}...")
                    try:
                        conn.execute(text(f"ALTER TABLE clients DROP COLUMN IF EXISTS {col_name}"))
                        logger.info(f"✓ Column {col_name} dropped")
                    except Exception as e:
                        logger.warning(f"Could not drop column {col_name}: {e}")
        
        # Проверяем что таблицы созданы
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
            ))
            tables = result.fetchall()
            logger.info(f"✓ Tables in database: {[t[0] for t in tables]}")
            
            # Проверяем финальную структуру clients
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'clients'
                ORDER BY ordinal_position
            """))
            final_columns = [row[0] for row in result.fetchall()]
            logger.info(f"✓ Final clients table columns: {final_columns}")
        
        # Не загружаем клиентов автоматически - они будут загружены через endpoint загрузки CSV
        logger.info("✓ Database initialized. Clients will be loaded via CSV upload endpoint.")
    
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        raise

async def test_db_connection():
    """Тест подключения к БД"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✓ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise
