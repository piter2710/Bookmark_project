from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


bookmark_tags = Table(
    'bookmark_tags', Base.metadata,
    Column('bookmark_id', UUID(as_uuid=True), ForeignKey('bookmarks.id')),
    Column('tag_id', UUID(as_uuid=True), ForeignKey('tags.id'))
)

class Users(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String(20), default='user')
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    bookmarks = relationship("Bookmarks", back_populates="user", cascade="all, delete")

class Bookmarks(Base):
    __tablename__ = 'bookmarks'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), index=True)
    description = Column(String(500))
    url = Column(String(500), index=True)
    is_private = Column(Boolean, default=False)
    clicks = Column(Integer, default=0)
    archived = Column(Boolean, default=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("Users", back_populates="bookmarks")
    tags = relationship("Tags", secondary=bookmark_tags, back_populates="bookmarks")

class Tags(Base):
    __tablename__ = 'tags'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, index=True)  # Enforce uniqueness
    created_at = Column(DateTime, default=datetime.utcnow)

    bookmarks = relationship("Bookmarks", secondary=bookmark_tags, back_populates="tags")