from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.history import add_history_news, fetch_history_news_list, fetch_history_news_list_count, \
    remove_history_news_item_by_user, remove_all_history_news_by_user
from models.users import User
from schemas.history import HistoryAddedResponse, HistoryNewsItemResponse, HistoryNewsListResponse, HistoryAddRequest
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])

@router.post("/add")
async def add_history(
        history_add_request: HistoryAddRequest,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
        ):
    result = await add_history_news(db, user.id, history_add_request.news_id)
    return success_response(message="添加成功",
                            data=HistoryAddedResponse.model_validate(result).model_dump(by_alias=True))

@router.get("/list")
async def get_history_list(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
        page: int = Query(1, ge=1, alias="page"),
        page_size: int = Query(10, ge=1, le=100, alias="pageSize")
        ):
    offset = (page-1)*page_size
    history_news_list = await fetch_history_news_list(db, user.id, offset, page_size)
    total = await fetch_history_news_list_count(db, user.id)
    has_more = total > offset + page_size

    items = [HistoryNewsItemResponse.model_validate(row) for row in history_news_list]

    response = HistoryNewsListResponse(list=items, total=total, hasMore=has_more)
    return success_response(data=response.model_dump(by_alias=True))

@router.delete("/delete/{history_id}")
async def delete_history_item(
        history_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
        ):
    await remove_history_news_item_by_user(db, user.id, history_id)
    return success_response(message = "删除成功", data = None)

@router.delete("/clear")
async def clear_history(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
        ):
    await remove_all_history_news_by_user(db, user.id)
    return success_response(message = "清空成功", data = None)
