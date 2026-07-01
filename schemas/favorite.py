from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.news import NewsListResponse

class FavoriteAddRequest(BaseModel):
    news_id: int = Field(alias="newsId")


class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(alias="isFavorite")

class FavoriteResponse(BaseModel):
    id: int
    news_id: int
    user_id: int
    created_at: datetime
    model_config = ConfigDict(
        from_attributes = True,
        populate_by_name = True
    )


class FavoriteNewsItemResponse(NewsListResponse):
    created_at: datetime = Field(alias="favoriteTime")



class FavoriteListResponse(BaseModel):
    list: list[FavoriteNewsItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore")

