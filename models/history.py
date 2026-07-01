from datetime import datetime, timezone

from sqlalchemy import Integer, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseBase


class History(BaseBase):
    __tablename__ = "history"
    __table_args__ = (
        UniqueConstraint("user_id", "news_id", name="uq_history_user_news"),
        Index("idx_history_user_id", "user_id"),
        Index("idx_history_news_id", "news_id"),
        Index("idx_history_view_time", "view_time"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="历史ID")
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.id'),
        nullable=False,
        comment="用户ID")
    news_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('news.id'),
        nullable=False,
        comment="新闻ID")
    view_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="浏览时间")

    def __repr__(self):
        return f"<History(id={self.id}, user_id={self.user_id}, news_id={self.news_id}, view_time={self.view_time})>"