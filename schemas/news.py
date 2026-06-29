from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class NewsListResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    image: Optional[str]
    author: Optional[str]
    category_id: int = Field(alias="categoryId")
    views: int
    publish_time: Optional[datetime] = Field(None, alias="publishedTime")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class NewsDetailResponse(BaseModel):
    id: int
    title: str
    content: str
    image: Optional[str] = None
    author: Optional[str] = None
    publish_time: Optional[datetime] = Field(None, alias="publishTime")
    category_id: int = Field(alias="categoryId")
    views: int

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
