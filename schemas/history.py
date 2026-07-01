from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.news import NewsListResponse


class HistoryAddRequest(BaseModel):
    news_id: int = Field(alias="newsId")


class HistoryAddedResponse(BaseModel):
    id: int
    user_id: int = Field(alias="userId")
    news_id: int = Field(alias="newsId")
    view_time: datetime = Field(alias="viewTime")
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class HistoryNewsItemResponse(NewsListResponse):
    view_time: datetime = Field(alias="viewTime")


class HistoryNewsListResponse(BaseModel):
    list: list[HistoryNewsItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore")
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )