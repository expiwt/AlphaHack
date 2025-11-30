from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings, ALLOWED_ORIGINS
from app.core.logging_config import setup_logging
from app.api.v1.endpoints import health, auth, clients, predictions, dashboard
from app.data.database import init_db, test_db_connection

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    logger.info("="*60)
    logger.info("🚀 STARTING ALFA-BANK INCOME PREDICTION API")
    logger.info("="*60)
    
    try:
        # 1. Test database connection
        logger.info("📊 Testing database connection...")
        await test_db_connection()
        
        # 2. Initialize database
        logger.info("📊 Initializing database...")
        await init_db()
        
        logger.info("="*60)
        logger.info("✅ APPLICATION STARTED SUCCESSFULLY!")
        logger.info("="*60)
        logger.info(f"📍 API URL: http://localhost:8000")
        logger.info(f"📍 API Docs: http://localhost:8000/docs")
        logger.info(f"📍 Frontend: http://localhost:3000")
        logger.info("="*60)
    
    except Exception as e:
        logger.error(f"❌ STARTUP ERROR: {e}")
        raise
    
    yield
    
    # SHUTDOWN
    logger.info("🛑 Shutting down application...")

app = FastAPI(
    title="Alfa-Bank Income Prediction API",
    description="API для прогноза доходов клиентов",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://178.72.152.189", "http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTES
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(clients.router, prefix="/api/v1", tags=["clients"])
app.include_router(predictions.router, prefix="/api/v1", tags=["predictions"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["dashboard"])

@app.get("/")
async def root():
    return {
        "message": "Alfa-Bank Income Prediction API",
        "version": "1.0.0",
        "status": "🟢 Running",
        "docs": "http://localhost:8000/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
