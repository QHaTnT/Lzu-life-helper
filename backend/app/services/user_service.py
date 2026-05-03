"""
用户服务 - 认证与用户管理
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models import User, UserRole
from app.core.security import verify_password, get_password_hash
from app.schemas.user import UserCreate


class UserService:
    """用户服务"""

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """用户认证"""
        # 支持用户名或学号登录
        user = (
            db.query(User)
            .filter(
                (User.username == username) | (User.student_id == username)
            )
            .first()
        )

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        existing_user = (
            db.query(User)
            .filter(
                (User.username == user_data.username)
                | (User.student_id == user_data.student_id)
            )
            .first()
        )

        if existing_user:
            raise ValueError("用户名或学号已存在")

        # 创建用户
        user = User(
            student_id=user_data.student_id,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password),
            real_name=user_data.real_name,
            phone=user_data.phone,
            email=user_data.email,
            role=UserRole.STUDENT,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def update_user(db: Session, user_id: int, update_data: dict) -> Optional[User]:
        """更新用户信息"""
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return None

        for key, value in update_data.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)

        db.commit()
        db.refresh(user)

        return user
