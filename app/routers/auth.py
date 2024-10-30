from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from app.database import get_db
from app.models import User
from pydantic import BaseModel

from app.schemas import UserCreate

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await db.execute(select(User).filter(User.username == user.username))
    existing_user = existing_user.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = pwd_context.hash(user.password)
    new_user = User(username=user.username, password_hash=hashed_password)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"id": new_user.id, "username": new_user.username}


@router.post("/login")
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    user_record = await db.execute(select(User).filter(User.username == user.username))
    user_record = user_record.scalars().first()

    if not user_record or not pwd_context.verify(user.password, user_record.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {"id": user_record.id, "username": user_record.username}
