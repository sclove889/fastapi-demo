from datetime import datetime, timezone

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News


async def add_history_news(db: AsyncSession, user_id: int, news_id: int):
    # 1. 先查这个 (user, news) 组合有没有存过
    stmt = select(History).where(
        History.user_id == user_id,
        History.news_id == news_id,
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()

    # 2. 存过 → 只更新浏览时间
    if existing:
        existing.view_time = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(existing)
        return existing

    # 3. 没存过 → 新增
    history = History(user_id=user_id, news_id=news_id)
    db.add(history)
    await db.flush()
    await db.refresh(history)
    return history

async def fetch_history_news_list(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10):
    stmt = (select(News.id,News.title,News.description,News.image,News.author,News.publish_time,
                   News.category_id,News.views,History.view_time)
            .join(History,History.news_id == News.id)
            .where(History.user_id == user_id)
            .offset(skip)
            .limit(limit))
    result = await db.execute(stmt)
    return result.all()

async def fetch_history_news_list_count(db: AsyncSession, user_id: int):
    stmt = select(func.count()).select_from(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one()

async def remove_history_news_item_by_user(db: AsyncSession, user_id: int, history_id: int):
    stmt = delete(History).where(History.id == history_id, History.user_id == user_id)
    result = await db.execute(stmt)
    return result.rowcount > 0

async def remove_all_history_news_by_user(db: AsyncSession, user_id: int):
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    return result.rowcount

