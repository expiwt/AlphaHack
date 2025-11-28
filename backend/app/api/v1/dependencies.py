from fastapi import Depends, HTTPException, Header
from typing import Optional
from app.core.security import verify_token

async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Проверить JWT токен и вернуть текущего пользователя
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    # Извлекаем токен из "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    # Проверяем токен
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"email": email}

# ML зависимости
_model_loader = None
_cache = None

def init_dependencies():
    global _model_loader, _cache
    from app.ml.model_loader import ModelLoader
    from app.data.cache import CacheManager
    
    _model_loader = ModelLoader("/app/models")
    _cache = CacheManager()
    print("✓ Dependencies initialized")

def get_model_loader():
    return _model_loader

def get_cache():
    return _cache
