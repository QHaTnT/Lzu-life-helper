"""
用户认证 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token
from app.core.response import ok
from app.schemas.user import UserCreate, UserLogin, UserUpdate
from app.services.user_service import UserService
from app.api.deps import get_current_active_user
from app.models import User
from app.utils.serializers import serialize_user

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        user = UserService.create_user(db, user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return ok(serialize_user(user), msg="注册成功")


@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = UserService.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )

    # JWT spec: sub 必须是字符串
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return ok(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": serialize_user(user),
        },
        msg="登录成功",
    )


@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return ok(serialize_user(current_user))


@router.put("/me")
def update_current_user(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新当前用户信息"""
    update_dict = update_data.model_dump(exclude_unset=True)
    user = UserService.update_user(db, current_user.id, update_dict)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return ok(serialize_user(user), msg="更新成功")
