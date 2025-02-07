from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from models import Bookmarks, Tags, Users
from database import get_db
from auth import get_current_user
from utilities import auto_tag_bookmark
from schemas import BookmarkBase, BookmarkCreate, BookmarkUpdate, BookmarkResponse

Brouter = APIRouter(
    prefix="/bookmarks",
    tags=["Bookmarks"]
)


@Brouter.get("/", response_model=List[BookmarkResponse])
async def get_bookmarks(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    bookmarks = db.query(Bookmarks).filter(Bookmarks.user_id == current_user.id).all()
    return bookmarks


@Brouter.get("/{bookmark_id}", response_model=BookmarkResponse)
async def get_bookmark(
    bookmark_id: UUID,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    bookmark = (
        db.query(Bookmarks)
          .filter(Bookmarks.id == bookmark_id, Bookmarks.user_id == current_user.id)
          .first()
    )
    if not bookmark:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    return bookmark


@Brouter.post("/", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    bookmark_in: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    new_bookmark = Bookmarks(
        url=bookmark_in.url,
        title=bookmark_in.title,
        description=bookmark_in.description,
        is_private=bookmark_in.is_private,
        user_id=current_user.id
    )
    if bookmark_in.tags:
        tag_names = bookmark_in.tags
    else:
        tag_names = auto_tag_bookmark(
            bookmark_in.url,
            bookmark_in.title or "",
            bookmark_in.description or ""
        )
    tag_objects = []
    for name in tag_names:
        tag = db.query(Tags).filter(Tags.name == name).first()
        if not tag:
            tag = Tags(name=name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        tag_objects.append(tag)
    new_bookmark.tags = tag_objects

    db.add(new_bookmark)
    db.commit()
    db.refresh(new_bookmark)
    return new_bookmark


@Brouter.put("/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: UUID,
    bookmark_update: BookmarkUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    bookmark = (
        db.query(Bookmarks)
          .filter(Bookmarks.id == bookmark_id, Bookmarks.user_id == current_user.id)
          .first()
    )
    if not bookmark:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    if bookmark_update.title is not None:
        bookmark.title = bookmark_update.title
    if bookmark_update.description is not None:
        bookmark.description = bookmark_update.description
    if bookmark_update.is_private is not None:
        bookmark.is_private = bookmark_update.is_private
    if bookmark_update.archived is not None:
        bookmark.archived = bookmark_update.archived

    db.commit()
    db.refresh(bookmark)
    return bookmark


@Brouter.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    bookmark_id: UUID,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    bookmark = (
        db.query(Bookmarks)
          .filter(Bookmarks.id == bookmark_id, Bookmarks.user_id == current_user.id)
          .first()
    )
    if not bookmark:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    db.delete(bookmark)
    db.commit()
    return


@Brouter.post("/{bookmark_id}/click", response_model=BookmarkResponse)
async def increment_click(
    bookmark_id: UUID,
    db: Session = Depends(get_db)
):
    bookmark = db.query(Bookmarks).filter(Bookmarks.id == bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    bookmark.clicks += 1
    db.commit()
    db.refresh(bookmark)
    return bookmark
