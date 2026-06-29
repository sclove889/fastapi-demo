from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud.favorite import check_favorite_news_by_user, add_favorite_news_by_user, remove_favorite_news_by_user, \
    fetch_favorite_news_list, fetch_favorite_news_list_count, remove_all_favorite_news_by_user
from models.users import User
from schemas.favorite import FavoriteResponse, FavoriteListResponse, FavoriteCheckResponse, FavoriteNewsItemResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/favorite", tags=["favorite"])

@router.get("/check")
async def check_favorite_news(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
        news_id: int = Query(..., alias="newsId")
        ):
    result = await check_favorite_news_by_user(db, user.id, news_id)
    result_data = FavoriteCheckResponse(isFavorite = result).model_dump(by_alias=True)
    return success_response(data = result_data)


@router.post("/add")
async def add_favorite_news(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
        news_id: int = Query(..., alias="newsId")
        ):
    result = await add_favorite_news_by_user(db, user.id, news_id)
    favorite_news = FavoriteResponse.model_validate(result).model_dump(by_alias=True)
    return success_response(message="收藏成功", data=favorite_news)

@router.delete("/remove")
async def remove_favorite_news(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
        news_id: int = Query(..., alias="newsId")
        ):
    result = await remove_favorite_news_by_user(db, user.id, news_id)
    return success_response(message = "取消收藏成功", data = None)

@router.get("/list")
async def get_favorite_news_list(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
        page: int = Query(1, ge=1, alias="page"),
        page_size: int = Query(10, le=100, alias="pageSize")
        ):
    offset = (page-1)*page_size
    news_list = await fetch_favorite_news_list(db, user.id, offset, page_size)
    total = await fetch_favorite_news_list_count(db, user.id)
    has_more = total > offset + page_size
    # 先把每一条 Row 验证成 FavoriteNewsItemResponse（这一步用 model_validate , 因为每个 Row 对得上单条 schema）
    items = [FavoriteNewsItemResponse.model_validate(row) for row in news_list]

    # 把三样东西装进 FavoriteListResponse —— 直接传参，不用 model_validate
    response = FavoriteListResponse(list=items, total=total, hasMore=has_more)

    return success_response(data=response.model_dump(by_alias=True))



@router.delete("/clear")
async def clear_favorite_news(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
        ):
    await remove_all_favorite_news_by_user(db, user.id)
    return success_response(message = "清空成功", data = None)





