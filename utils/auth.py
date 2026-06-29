from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud.users import get_user_by_token

security = HTTPBearer ()

async def get_current_user(
        db : AsyncSession = Depends(get_db),
        creds: HTTPAuthorizationCredentials = Depends(security)
        ):
    user = await get_user_by_token(db, creds.credentials)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user

