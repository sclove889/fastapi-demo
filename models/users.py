from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.orm import  Mapped, mapped_column

from models.base import BaseBase


class Base(BaseBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        comment="创建时间")


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="用户ID")

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="用户名")

    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="密码（加密存储）")

    nickname: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="昵称")


    avatar: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="头像URL",
        default='https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg')


    gender: Mapped[Optional[str]] = mapped_column(
        Enum('male', 'female', 'unknown'),
        comment="性别",
        default='unknown')


    bio: Mapped[Optional[str]] = mapped_column(
        String(500),
        comment="个人简介",
        default='这个人很懒，什么都没留下')

    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        unique=True,
        comment="手机号")

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="更新时间")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class UserToken(Base):
    __tablename__ = "user_token"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="令牌ID")

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(User.id),
        nullable=False,
        comment="用户ID")

    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        comment="访问令牌")

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="令牌过期时间")


    def __repr__(self):
        return f"<UserToken(id={self.id}, user_id={self.user_id})>"