from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News


async def check_favorite_news_by_user(db:AsyncSession, user_id:int, news_id:int):
    stmt = select(Favorite).where(Favorite.news_id == news_id, Favorite.user_id == user_id)
    result = await db.execute(stmt)
    favorite = result.scalar_one_or_none()
    return bool(favorite)

async def add_favorite_news_by_user(db:AsyncSession, user_id:int, news_id:int):
    from fastapi import HTTPException, status

    # 检查新闻是否存在
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="新闻不存在")

    # 检查是否已收藏
    already_favorite = await check_favorite_news_by_user(db, user_id, news_id)
    if already_favorite:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="已收藏该新闻")

    # 添加收藏
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.flush()
    await db.refresh(favorite)
    return favorite

async def remove_favorite_news_by_user(db:AsyncSession, user_id:int, news_id:int):
    stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    return result.rowcount > 0

async def fetch_favorite_news_list(db:AsyncSession, user_id:int, skip:int = 0, limit:int = 10):
    stmt = (select(News.id,News.title,News.description,News.image,News.author,News.publish_time,
                   News.category_id,News.views,Favorite.created_at)
            .join(Favorite,Favorite.news_id == News.id)
            .where(Favorite.user_id == user_id)
            .offset(skip)
            .limit(limit))
    result = await db.execute(stmt)
    return result.all()

async def fetch_favorite_news_list_count(db:AsyncSession, user_id:int):
    stmt = select(func.count(News.id)).select_from(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one()

async def remove_all_favorite_news_by_user(db:AsyncSession, user_id:int):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    return result.rowcount








