"""认证相关业务逻辑。"""
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def create_token(user: User) -> str:
    return create_access_token(subject=str(user.id))


def bootstrap_admin(db: Session) -> None:
    """启动时若管理员不存在则创建。"""
    exists = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
    if exists:
        return
    admin = User(
        username=settings.ADMIN_USERNAME,
        email=settings.ADMIN_EMAIL,
        password_hash=hash_password(settings.ADMIN_PASSWORD),
        role="admin",
    )
    db.add(admin)
    db.commit()


def change_password(db: Session, user: User, old_password: str, new_password: str) -> bool:
    if not verify_password(old_password, user.password_hash):
        return False
    user.password_hash = hash_password(new_password)
    db.add(user)
    db.commit()
    return True
