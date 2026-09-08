import os
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from models import AdminUser

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "cbs-school-fallback-secret-key-production-2026")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_admin(db: Session, username: str, password: str) -> Optional[AdminUser]:
    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not admin:
        return None
    if not verify_password(password, admin.password_hash):
        return None
    if not admin.is_active:
        return None
    return admin


async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> AdminUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if admin is None or not admin.is_active:
        raise credentials_exception
    return admin
