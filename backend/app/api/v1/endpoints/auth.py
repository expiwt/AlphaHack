from fastapi import APIRouter, HTTPException, Depends
from app.api.v1.schemas import UserLogin, UserRegister, Token
from app.core.security import create_access_token, verify_password, hash_password
from app.data.database import SessionLocal
from app.data.models import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/auth/register", response_model=Token)
async def register(user_data: UserRegister):
    """
    Регистрация нового пользователя
    """
    db = SessionLocal()
    try:
        # Проверяем что пользователь не существует
        existing = db.query(User).filter_by(email=user_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Создаем пользователя
        hashed_pw = hash_password(user_data.password)
        user = User(
            email=user_data.email,
            password_hash=hashed_pw,
            full_name=user_data.full_name
        )
        
        db.add(user)
        db.commit()
        
        logger.info(f"✓ User registered: {user_data.email}")
        
        # Создаем JWT токен
        access_token = create_access_token(data={"sub": user_data.email})
        return Token(access_token=access_token)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()

@router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Аутентификация пользователя
    """
    db = SessionLocal()
    try:
        # Ищем пользователя
        user = db.query(User).filter_by(email=credentials.email).first()
        
        if not user or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        logger.info(f"✓ User logged in: {credentials.email}")
        
        # Создаем JWT токен
        access_token = create_access_token(data={"sub": credentials.email})
        return Token(access_token=access_token)
    
    finally:
        db.close()
