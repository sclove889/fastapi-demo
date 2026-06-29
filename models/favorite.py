from datetime import datetime, timezone

from sqlalchemy import Integer, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import mapped_column, Mapped

from models.base import BaseBase


class Favorite(BaseBase):
    __tablename__ = "favorite"
    __table_args__ = (
        UniqueConstraint("user_id", "news_id", name="user_news_unique"),
        Index('idx_favorite_user_id', 'user_id'),
        Index('idx_favorite_news_id', 'news_id'),
    )
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="收藏ID")
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id"),
        nullable=False,
        comment="用户ID")
    news_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("news.id"),
        nullable=False,
        comment="新闻ID")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        comment="创建时间")

    def __repr__(self):
        return f"<Favorite(id={self.id}, user_id={self.user_id}, news_id={self.news_id})>"