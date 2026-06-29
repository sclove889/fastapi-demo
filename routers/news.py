from fastapi import APIRouter, Query, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud.news import fetch_categories, fetch_news_list, fetch_news_count, fetch_news_detail, update_news_views, \
    fetch_recommended_news
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

    recommended_news = await fetch_recommended_news(db, news_detail.category_id, news_id)

    news_data = NewsDetailResponse.model_validate(news_detail).model_dump(by_alias=True)
    news_data["relatedNews"] = recommended_news
    return success_response(data=news_data)

