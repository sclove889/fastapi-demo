from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.users import get_user_by_token

# 直接读取 Authorization 请求头，接受裸 token（不带 Bearer 前缀），符合 API 规范
security = APIKeyHeader(name="Authorization")

async def get_current_user(
        db : AsyncSession = Depends(get_db),
        token: str = Depends(security)
        ):
    user = await get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user

