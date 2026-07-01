from fastapi import APIRouter, Query, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.news import fetch_categories, fetch_news_list, fetch_news_count, fetch_news_detail, update_news_views, \
    fetch_recommended_news, fetch_news_views, fetch_news_views_batch
from schemas.news import NewsDetailResponse, NewsListResponse
from utils.response import success_response

router = APIRouter(prefix="/api/news", tags=["news"])

#接口实现流程
#1.模块化路由→API接口规范文档
#2.定义模型类→数据库表（数据库设计文档）
#3.在crud文件夹里面创建文件，封装操作数据库的方法
#4.在路由处理函数里面调用crud封装好的方法，响应结果

@router.get("/categories")
async def get_categories(db : AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    categories = await fetch_categories(db, skip, limit)
    return success_response(data = categories)

@router.get("/list")
async def get_news_list(
        db : AsyncSession = Depends(get_db),
        category_id: int = Query(...,alias="categoryId"),
        page: int = Query(1,ge=1,alias="page"),
        page_size: int = Query(10,le=100,alias="pageSize")
        ):
    offset = (page-1)*page_size
    news_list = await fetch_news_list(db, category_id, offset, page_size)
    total = await fetch_news_count(db, category_id)
    has_more = total > offset + page_size
    news_list_data = {
        "list": [NewsListResponse.model_validate(n).model_dump(by_alias=True) for n in news_list],
        "total": total,
        "hasMore": has_more,
    }
    # 缓存里的 views 是旧值，用数据库最新阅读数逐条覆盖
    if news_list_data["list"]:
        ids = [item["id"] for item in news_list_data["list"]]
        views_map = await fetch_news_views_batch(db, ids)
        for item in news_list_data["list"]:
            item["views"] = views_map.get(item["id"], 0)
    return success_response(data = news_list_data)


@router.get("/detail")
async def get_news_detail(
        db : AsyncSession = Depends(get_db),
        news_id: int = Query(...,alias="id")
        ):
    news_detail = await fetch_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")

    views_result = await update_news_views(db, news_id)

    # 先统一转成 Pydantic 模型：model_validate 对 ORM 对象和缓存 dict 都适用，
    # 之后从模型上取 category_id，避免 dict 没有 .category_id 属性导致 500
    news_model = NewsDetailResponse.model_validate(news_detail)

    recommended_news = await fetch_recommended_news(db, news_model.category_id, news_id)

    news_data = news_model.model_dump(by_alias=True)
    # 缓存里的 views 是旧值，用数据库最新阅读数覆盖，保证每次返回的阅读数都是实时的
    news_data["views"] = await fetch_news_views(db, news_id)
    news_data["relatedNews"] = recommended_news
    return success_response(data=news_data)

