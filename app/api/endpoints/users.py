from datetime import datetime, timedelta
from typing import Annotated, List

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, select, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship, backref

from app.api.schemas.user import UserResponse, UserCreate, ResidentInfo, ResidentUpdate, Token, ResidentCreate
from app.api.models.models import User, Resident
from app.config import settings, engine, SessionLocal, oauth2_scheme
from app.database import get_db

import bcrypt
import jwt

router = APIRouter()


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    user = db.execute(select(User).where(User.username == username)).scalars().first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


# Hashing Function
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


# Token Creation
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# Authentication Function
def authenticate_user(db: Session, username: str, password: str):
    user = db.execute(select(User).where(User.username == username)).scalars().first()
    if not user:
        return None
    if bcrypt.checkpw(password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        return user
    return None


# API Endpoints
# Auth Endpoints
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["account managing"])
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.execute(select(User).where(User.username == user.username)).scalars().first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    db_resident = Resident(
        user_id=new_user.id,
        surname=user.surname,
        name=user.name,
        birthdate=user.birthdate,
        email=user.email,
        phone=user.phone,
    )
    db.add(db_resident)
    db.commit()
    db.refresh(db_resident)

    return new_user


@router.post("/token", response_model=Token, tags=["account managing"])
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserResponse, tags=["resident panel"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.post("/residents/", response_model=ResidentInfo, status_code=status.HTTP_201_CREATED, tags=["account managing"])
def create_resident(resident: ResidentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_resident = Resident(**resident.dict())
    db.add(db_resident)
    db.commit()
    db.refresh(db_resident)
    return db_resident


@router.get("/residents/all", response_model=List[ResidentInfo], tags=["resident panel"])
def read_resident(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
        Retrieves information for all residents.
    """
    residents = db.execute(select(Resident).order_by(Resident.surname, Resident.name)).scalars().all()
    return residents


@router.get("/residents/{resident_id}", response_model=ResidentInfo, tags=["resident panel"])
def read_resident(resident_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    resident = db.execute(select(Resident).where(Resident.id == resident_id)).scalars().first()
    if resident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")
    return resident
