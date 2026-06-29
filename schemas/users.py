from typing import Optional, Literal

from pydantic import BaseModel, Field, ConfigDict


class UserRequest(BaseModel):
    username: str
    password: str

class UserInfoOptional(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像")
    gender: Optional[Literal['male', 'female', 'unknown']] = Field(None, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个⼈简介")

class UserInfo(UserInfoOptional):
    id: int
    username: str
    model_config = ConfigDict(
        from_attributes=True  # 允许从 ORM 对象属性中取值
    )

class UserAuthResponse(BaseModel):
    token: str
    userInfo: UserInfo
    model_config = ConfigDict(
        populate_by_name=True,  # alias / 字段名兼容
        from_attributes=True  # 允许从 ORM 对象属性中取值
    )

class UserUpdateRequest(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像")
    gender: Optional[Literal['male', 'female', 'unknown']] = Field(None, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个⼈简介")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")

class UserChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1, max_length=72, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=72, description="新密码")