from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=8)

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    role: str
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


class TagBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)

    @validator('name')
    def lowercase_name(cls, v):
        return v.lower()

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class BookmarkBase(BaseModel):
    url: str = Field(..., max_length=500)
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    is_private: bool = False

class BookmarkCreate(BookmarkBase):
    tags: List[str] = []

class BookmarkUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    is_private: Optional[bool] = None
    archived: Optional[bool] = None

class BookmarkResponse(BookmarkBase):
    id: UUID
    clicks: int
    archived: bool
    created_at: datetime
    user: UserResponse
    tags: List[TagResponse]

    class Config:
        orm_mode = True


class PopularBookmarkResponse(BaseModel):
    id: UUID
    title: str
    url: str
    clicks: int

class TagCloudResponse(BaseModel):
    name: str
    count: int

class AdminUserResponse(UserResponse):
    bookmarks: List[BookmarkResponse]

    class Config:
        orm_mode = True

class UserStatusUpdate(BaseModel):
    is_active: bool