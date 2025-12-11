from datetime import datetime, timedelta
from typing import Annotated, List

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, select, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship, backref

from app.api.endpoints.users import get_current_active_user
from app.api.models.models import User, News, Resident, Coach, TrainingType, TrainingSession, ResidentToTraining, \
    Achievement, ResidentToAchievement
from app.api.schemas.item import NewsInfo, CoachInfo, TrainingSessionInfo, TrainingSessionInfoWithResidents, \
    TrainingTypeInfo, AchievementInfo, TrainingTypeStatistics, TrainingSessionShortInfo, TrainingSessionUpdate, \
    TrainingTypeUpdate, AchievementUpdate, CoachUpdate, NewsUpdate
from app.api.schemas.user import ResidentInfo, ResidentUpdate

from app.database import get_db


router = APIRouter()


@router.put("/residents/{resident_id}", response_model=ResidentInfo, tags=["resident panel"])
def update_resident(resident_id: int, resident_update: ResidentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Updates a resident's information.
    """
    db_resident = db.execute(select(Resident).where(Resident.id == resident_id)).scalars().first()
    if db_resident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")

    # Update fields if they are provided in the request
    if resident_update.surname is not None:
        db_resident.surname = resident_update.surname
    if resident_update.name is not None:
        db_resident.name = resident_update.name
    if resident_update.birthdate is not None:
        db_resident.birthdate = resident_update.birthdate
    if resident_update.email is not None:
        db_resident.email = resident_update.email
    if resident_update.phone is not None:
        db_resident.phone = resident_update.phone

    db.commit()
    db.refresh(db_resident)
    return db_resident


@router.put("/training_sessions/{session_id}", response_model=TrainingSessionShortInfo, tags=["training sessions endpoints"])
def update_training_session(
    session_id: int,
    session_update: TrainingSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Updates a training session's information.
    """
    db_session = db.execute(select(TrainingSession).where(TrainingSession.id == session_id)).scalars().first()
    if db_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training Session not found")

    # Update fields if they are provided in the request
    if session_update.training_type_id is not None:
        db_session.training_type_id = session_update.training_type_id
    if session_update.coach_id is not None:
        db_session.coach_id = session_update.coach_id
    if session_update.start_time is not None:
        db_session.start_time = session_update.start_time
    if session_update.duration is not None:
        db_session.duration = session_update.duration
    if session_update.max_capacity is not None:
        db_session.max_capacity = session_update.max_capacity

    db.commit()
    db.refresh(db_session)
    return db_session


@router.put("/training_types/{type_id}", response_model=TrainingTypeInfo, tags=["training types endpoints"])
def update_training_type(
    type_id: int,
    type_update: TrainingTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Updates a training type's information.
    """
    db_type = db.execute(select(TrainingType).where(TrainingType.id == type_id)).scalars().first()
    if db_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training Type not found")

    # Update fields if they are provided in the request
    if type_update.training_name is not None:
        db_type.training_name = type_update.training_name
    if type_update.description is not None:
        db_type.description = type_update.description

    db.commit()
    db.refresh(db_type)
    return db_type


@router.put("/achievements/{achievement_id}", response_model=AchievementInfo, tags=["achievements endpoints"])
def update_achievement(
    achievement_id: int,
    achievement_update: AchievementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Updates an achievement's information.
    """
    db_achievement = db.execute(select(Achievement).where(Achievement.id == achievement_id)).scalars().first()
    if db_achievement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Achievement not found")

    # Update fields if they are provided in the request
    if achievement_update.achievement_name is not None:
        db_achievement.achievement_name = achievement_update.achievement_name
    if achievement_update.description is not None:
        db_achievement.description = achievement_update.description
    if achievement_update.criteria is not None:
        db_achievement.criteria = achievement_update.criteria

    db.commit()
    db.refresh(db_achievement)
    return db_achievement


@router.put("/coaches/{coach_id}", response_model=CoachInfo, tags=["coaches endpoints"])
def update_coach(
    coach_id: int,
    coach_update: CoachUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Updates a coach's information.
    """
    db_coach = db.execute(select(Coach).where(Coach.id == coach_id)).scalars().first()
    if db_coach is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coach not found")

    # Update fields if they are provided in the request
    if coach_update.surname is not None:
        db_coach.surname = coach_update.surname
    if coach_update.name is not None:
        db_coach.name = coach_update.name
    if coach_update.speciality is not None:
        db_coach.speciality = coach_update.speciality
    if coach_update.qualification is not None:
        db_coach.qualification = coach_update.qualification
    if coach_update.extra_info is not None:
        db_coach.extra_info = coach_update.extra_info

    db.commit()
    db.refresh(db_coach)
    return db_coach


@router.put("/news/{news_id}", response_model=NewsInfo, tags=["news endpoints"])
def update_news(
    news_id: int,
    news_update: NewsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Updates a news post's information.
    """
    db_news = db.execute(select(News).where(News.id == news_id)).scalars().first()
    if db_news is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News post not found")

    # Update fields if they are provided in the request
    if news_update.post_title is not None:
        db_news.post_title = news_update.post_title
    if news_update.post_info is not None:
        db_news.post_info = news_update.post_info
    if news_update.post_image is not None:
        db_news.post_image = news_update.post_image
    if news_update.post_time is not None:
        db_news.post_time = news_update.post_time

    db.commit()
    db.refresh(db_news)

    return NewsInfo(
        id=db_news.id,
        username=db_news.user.username,
        post_title=db_news.post_title,
        post_info=db_news.post_info,
        post_image=db_news.post_image,
        post_time=db_news.post_time,
    )
