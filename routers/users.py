
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.users import get_user_data_by_username, create_user, generate_token, authenticate_user, update_user_info, \
    change_user_password
from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfo, UserUpdateRequest, UserChangePasswordRequest
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/user", tags=["user"])

@router.post("/register")
async def register(user_data: UserRequest, db : AsyncSession = Depends(get_db)):
    existing_user = await get_user_data_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    user = await create_user(db, user_data)
    user_token = await generate_token(db, user.id)

    user_data_response = UserAuthResponse(
        token=user_token.token,
        userInfo=UserInfo.model_validate(user)
        )
    return success_response("注册成功",user_data_response)


@router.post("/login")
async def login(user_data: UserRequest, db : AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    user_token = await generate_token(db, user.id)
    user_data_response = UserAuthResponse(
        token=user_token.token,
        userInfo=UserInfo.model_validate(user)
        )
    return success_response("登录成功",user_data_response)


@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    return success_response("获取用户信息成功",UserInfo.model_validate(user))

@router.post("/update")
async def update_user(
        user_data: UserUpdateRequest,
        db : AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
        ):
    user_updated = await update_user_info(db, user.id, user_data)

    return success_response("更新用户信息成功",UserInfo.model_validate(user_updated))


@router.post("/password")
async def change_password(
        user_data: UserChangePasswordRequest,
        db : AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
        ):
    await change_user_password(db, user.id, user_data.old_password, user_data.new_password)
    return success_response("修改密码成功")




