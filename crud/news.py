from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import NewsCategory, News


async def fetch_categories(db : AsyncSession, skip: int = 0, limit: int = 100):
    stmt = select(NewsCategory).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def fetch_news_list(db : AsyncSession, category_id: int, skip: int = 0, limit: int = 10):
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def fetch_news_count(db : AsyncSession, category_id: int):
    stmt = select(func.count()).select_from(News).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()

async def fetch_news_detail(db : AsyncSession, news_id: int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def update_news_views(db : AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views+1)
    result= await db.execute(stmt)
    return result.rowcount > 0

async def fetch_recommended_news(db : AsyncSession, category_id: int, news_id: int, limit: int = 5):
    stmt = (select(News).where(News.category_id == category_id, News.id != news_id)
            .order_by(News.views.desc(), News.publish_time.desc()).limit(limit))
    result = await db.execute(stmt)
    return [{
        "id": news.id,
        "title": news.title,
        "image": news.image,
        "author": news.author,
        "publishTime": news.publish_time,
        "categoryId": news.category_id,
        "views": news.views
    } for news in result.scalars().all()]




