
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException,status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest
from utils.security import get_hash_password, verify_password


async def get_user_data_by_username(db : AsyncSession, username: str):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(db : AsyncSession, user_data: UserRequest):
    user = User(
        username=user_data.username,
        password=get_hash_password(user_data.password)
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user

async def generate_token(db : AsyncSession, user_id):

    token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    # 检查用户是否已经存在令牌
    query = await db.execute(select(UserToken).where(UserToken.user_id == user_id))
    user_token = query.scalar_one_or_none()

    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
    else:
        user_token = UserToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        db.add(user_token)
    await db.flush()
    await db.refresh(user_token)
    return user_token

async def authenticate_user(db : AsyncSession, username: str, password: str):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    return user if user and verify_password(password, user.password) else None

async def get_user_by_token(db : AsyncSession, token: str):
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()
    if not user_token or user_token.expires_at < datetime.now(timezone.utc):
        return None
    query2 = select(User).where(User.id == user_token.user_id)
    result2 = await db.execute(query2)
    return result2.scalar_one_or_none()


async def get_user_by_id(db : AsyncSession, user_id):
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()



async def update_user_info(db : AsyncSession, user_id: int, user_data: UserUpdateRequest):
    try:
        # 构建更新数据
        update_values = user_data.model_dump(exclude_unset=True, exclude_none=True)

        if not update_values:
            # 没有要更新的字段，直接查询返回
            updated_user = await get_user_by_id(db, user_id)
            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )
            return updated_user

        # 执行更新
        query = update(User).where(User.id == user_id).values(**update_values)
        await db.execute(query)

        # 提交
        await db.commit()

        # 重新查询获取最新数据
        updated_user = await get_user_by_id(db, user_id)

        return updated_user

    except IntegrityError as e:
        # 回滚事务
        await db.rollback()

        # 判断是否是 phone 唯一约束冲突
        error_msg = str(e.orig).lower()
        if 'phone' in error_msg or '手机号' in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该手机号已被其他用户使用"
            )
        elif 'username' in error_msg or '用户名' in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户名已被使用"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="数据冲突，请检查输入后重试"
            )

    except HTTPException:
        # 重新抛出 HTTPException
        raise

    except Exception as e:
        # 回滚事务
        await db.rollback()

        # 记录日志（生产环境应该用 logging）
        print(f"更新用户信息失败: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误，请稍后重试"
        )


async def change_user_password(db: AsyncSession, user_id: int, old_password: str, new_password: str):
    user = await get_user_by_id(db, user_id)
    if not user or not verify_password(old_password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    query = update(User).where(User.id == user_id).values(password=get_hash_password(new_password))
    await db.execute(query)
    await db.flush()
    return await get_user_by_id(db, user_id)







