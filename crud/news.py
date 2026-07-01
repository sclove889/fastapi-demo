from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from cache.news import get_cached_categories, set_cache_categories, get_cache_news_list, set_cache_news_list, \
    get_cached_news_detail, cache_news_detail, get_cached_recommended_news, cache_recommended_news
from models.news import NewsCategory, News


async def fetch_categories(db : AsyncSession, skip: int = 0, limit: int = 100):
    # 先尝试从缓存中获取数据
    cached_categories = await get_cached_categories()
    if cached_categories:
        return cached_categories

    stmt = select(NewsCategory).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()  # ORM

    # 写入缓存
    if categories:
        categories = jsonable_encoder(categories)
        await set_cache_categories(categories)

    # 返回数据
    return categories

async def fetch_news_list(db : AsyncSession, category_id: int, skip: int = 0, limit: int = 10):
    cache_news_list = await get_cache_news_list(category_id, skip, limit)
    if cache_news_list:
        return cache_news_list

    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()

    if news_list:
        news_list = jsonable_encoder(news_list)
        await set_cache_news_list(category_id, skip, limit, news_list)

    return news_list

async def fetch_news_count(db : AsyncSession, category_id: int):
    stmt = select(func.count()).select_from(News).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()

async def fetch_news_detail(db : AsyncSession, news_id: int):
    if cached_news := await get_cached_news_detail(news_id):
        return cached_news

    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    news_detail = result.scalar_one_or_none()

    if news_detail:
        news_detail = jsonable_encoder(news_detail)
        await cache_news_detail(news_id, news_detail)

    return news_detail

async def update_news_views(db : AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views+1)
    result= await db.execute(stmt)
    return result.rowcount > 0

# 只查 views 一个字段，极轻量，用于 /detail 接口在 update_views 后获取最新阅读数
async def fetch_news_views(db: AsyncSession, news_id: int):
    stmt = select(News.views).where(News.id == news_id)
    result = await db.execute(stmt)
    row = result.scalar_one_or_none()
    return row if row is not None else 0

# 批量查 views，用于 /list 接口用最新阅读数覆盖缓存旧值，一次查询搞定整页
async def fetch_news_views_batch(db: AsyncSession, news_ids: list[int]) -> dict[int, int]:
    if not news_ids:
        return {}
    stmt = select(News.id, News.views).where(News.id.in_(news_ids))
    result = await db.execute(stmt)
    return {row[0]: row[1] for row in result.all()}

async def fetch_recommended_news(db : AsyncSession, category_id: int, news_id: int, limit: int = 5):
    if cached_recommended_news := await get_cached_recommended_news(category_id, news_id):
        return cached_recommended_news

    stmt = (select(News).where(News.category_id == category_id, News.id != news_id)
            .order_by(News.views.desc(), News.publish_time.desc()).limit(limit))
    result = await db.execute(stmt)
    recommended_news = [{
        "id": news.id,
        "title": news.title,
        "image": news.image,
        "author": news.author,
        "publishTime": news.publish_time,
        "categoryId": news.category_id,
        "views": news.views
    } for news in result.scalars().all()]

    if recommended_news:
        await cache_recommended_news(category_id, news_id, recommended_news)

    return recommended_news



