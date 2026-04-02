from datetime import datetime, timedelta

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_password, create_access_token
from app.repositories import user_repo


REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def authenticate(db: AsyncSession, email: str, password: str) -> dict | None:
    user = await user_repo.get_by_email(db, email)
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    token_data = {"sub": str(user.id), "role": user.role.name if user.role else None}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> dict | None:
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
    except JWTError:
        return None

    user = await user_repo.get_by_id(db, user_id)
    if not user or not user.is_active:
        return None

    token_data = {"sub": str(user.id), "role": user.role.name if user.role else None}
    new_access = create_access_token(token_data)
    new_refresh = create_refresh_token(token_data)
    return {
        "access_token": new_access,
        "token_type": "bearer",
        "refresh_token": new_refresh,
    }
