import uuid
from typing import Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.schemas.auth import UserRegisterRequest
from app.core.security import hash_password, verify_password

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    normalized_email = email.strip().lower()
    stmt = select(User).where(User.email == normalized_email)
    return db.execute(stmt).scalar_one_or_none()

def get_user_by_id(db: Session, user_id: Union[uuid.UUID, str]) -> Optional[User]:
    if isinstance(user_id, str):
        try:
            user_id = uuid.UUID(user_id)
        except (ValueError, TypeError):
            return None
    stmt = select(User).where(User.id == user_id)
    return db.execute(stmt).scalar_one_or_none()

def create_user(db: Session, user_in: UserRegisterRequest) -> User:
    normalized_email = user_in.email.strip().lower()
    hashed_pwd = hash_password(user_in.password)
    user = User(
        email=normalized_email,
        password_hash=hashed_pwd
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user