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
        
        # Проверяем что таблицы созданы
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
            ))
            tables = result.fetchall()
            logger.info(f"✓ Tables in database: {[t[0] for t in tables]}")
        
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
