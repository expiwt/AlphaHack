from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings
import hashlib
import os
import logging

logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """
    Хешировать пароль с помощью PBKDF2 (встроено в Python)
    """
    # Генерируем случайную соль
    salt = os.urandom(32)
    
    # Хешируем пароль
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    
    # Возвращаем соль + хеш в одной строке
    return salt.hex() + pwd_hash.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверить пароль
    """
    try:
        # Извлекаем соль из хешированного пароля
        salt = bytes.fromhex(hashed_password[:64])
        stored_hash = hashed_password[64:]
        
        # Хешируем введенный пароль с той же солью
        pwd_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode(), salt, 100000)
        
        # Сравниваем хеши
        return pwd_hash.hex() == stored_hash
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Создать JWT токен
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def verify_token(token: str) -> dict:
    """
    Проверить JWT токен
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {e}")
        return None
