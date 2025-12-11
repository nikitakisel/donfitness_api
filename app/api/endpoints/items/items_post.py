from datetime import datetime, timedelta
from typing import Annotated, List

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, select, ForeignKey, delete
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship, backref

from app.api.endpoints.users import get_current_active_user
from app.api.models.models import User, News, Resident, Coach, TrainingType, TrainingSession, ResidentToTraining, \
    Achievement, ResidentToAchievement
from app.api.schemas.item import NewsInfo, CoachInfo, TrainingSessionInfo, TrainingSessionInfoWithResidents, \
    TrainingTypeInfo, AchievementInfo, TrainingTypeStatistics, NewsCreate, CoachCreate, TrainingTypeCreate, \
    AchievementCreate, TrainingSessionCreate, ResidentToTrainingCreate

from app.database import get_db


router = APIRouter()


@router.post("/news/", response_model=None, status_code=status.HTTP_201_CREATED, tags=["news endpoints"])
def create_post(news: NewsCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_news = News(**news.dict())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news


@router.post("/coaches/", response_model=CoachInfo, status_code=status.HTTP_201_CREATED, tags=["coaches endpoints"])
def create_coach(coach: CoachCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_coach = Coach(**coach.dict())
    db.add(db_coach)
    db.commit()
    db.refresh(db_coach)
    return db_coach


@router.post("/training_types/", response_model=TrainingTypeInfo, status_code=status.HTTP_201_CREATED, tags=["training types endpoints"])
def create_training_type(training_type: TrainingTypeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_training_type = TrainingType(**training_type.dict())
    db.add(db_training_type)
    db.commit()
    db.refresh(db_training_type)
    return db_training_type


@router.post("/achievements/", response_model=AchievementInfo, status_code=status.HTTP_201_CREATED, tags=["achievements endpoints"])
def create_achievement(achievement: AchievementCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_achievement = Achievement(**achievement.dict())
    db.add(db_achievement)
    db.commit()
    db.refresh(db_achievement)
    return db_achievement


@router.post("/training_sessions/", response_model=None, status_code=status.HTTP_201_CREATED, tags=["training sessions endpoints"])
def create_training_session(training_session: TrainingSessionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_training_session = TrainingSession(**training_session.dict())
    db.add(db_training_session)
    db.commit()
    db.refresh(db_training_session)
    return db_training_session


# POST Endpoint for Resident to Training (Protected)
@router.post("/resident_to_training/", status_code=status.HTTP_201_CREATED, tags=["resident panel"])
def add_resident_to_training(resident_to_training: ResidentToTrainingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_resident_to_training = ResidentToTraining(**resident_to_training.dict())
    db.add(db_resident_to_training)
    db.commit()
    return {"message": "Resident added to training successfully"}
