from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models.user import User
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify


router_user = APIRouter(prefix='/user', tags=['user'])


@router_user.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


@router_user.get('/{user_id}')
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")
    return user


@router_user.post('/create')
async def create_user(user: CreateUser, db: Annotated[Session, Depends(get_db)]):
    new_user = User(**user.dict())
    db.execute(insert(User).values(new_user.__dict__))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router_user.put('/update/{user_id}')
async def create_user(user: CreateUser, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.execute(select(User).where(User.id == user.id)).scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="User  with this ID already exists")

    existing_username = db.execute(select(User).where(User.username == user.username)).scalar_one_or_none()
    if existing_username:
        raise HTTPException(status_code=400, detail="User  with this username already exists")

    new_user = User(**user.dict())
    db.execute(insert(User).values(new_user))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router_user.delete('/delete/{user_id}')
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    del_user = delete(User).where(User.id == user_id)
    result = db.execute(del_user)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User successfully deleted!'}