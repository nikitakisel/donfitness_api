from datetime import datetime, timedelta
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, select, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship, backref

from app.api.endpoints.users import get_current_active_user
from app.api.models.models import User, News, Resident, Coach, TrainingType, TrainingSession, ResidentToTraining, \
    Achievement, ResidentToAchievement

from app.database import get_db


router = APIRouter()


@router.delete("/resident_to_training/{resident_id}/{training_session_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["resident panel", "training sessions endpoints"])
def remove_resident_from_training(resident_id: int, training_session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Removes a resident from a training session.
    """
    db_resident_to_training = db.execute(
        select(ResidentToTraining).where(
            ResidentToTraining.resident_id == resident_id,
            ResidentToTraining.training_session_id == training_session_id
        )
    ).scalars().first()

    if db_resident_to_training is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident is not enrolled in this training session")

    db.delete(db_resident_to_training)
    db.commit()
    return


@router.delete("/training_sessions/{training_session_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["training sessions endpoints"])
def delete_training_session(training_session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Deletes a training session.
    """
    training_session = db.execute(
        select(TrainingSession).where(TrainingSession.id == training_session_id)
    ).scalars().first()

    if training_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training session not found")

    db.delete(training_session)
    db.commit()
    return


@router.delete("/training_types/{type_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["training types endpoints"])
def remove_training_type(type_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Removes a training type.
    """
    training_type = db.execute(
        select(TrainingType).where(TrainingType.id == type_id)
    ).scalars().first()

    if training_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Such training type is not exist")

    db.delete(training_type)
    db.commit()
    return


@router.delete("/achievements/{achievement_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["achievements endpoints"])
def remove_achievement(achievement_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Removes an achievement.
    """
    achievement = db.execute(
        select(Achievement).where(Achievement.id == achievement_id)
    ).scalars().first()

    if achievement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Such achievement is not exist")

    db.delete(achievement)
    db.commit()
    return


@router.delete("/coaches/{coach_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["coaches endpoints"])
def remove_coach(coach_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Removes a coach.
    """
    coach = db.execute(
        select(Coach).where(Coach.id == coach_id)
    ).scalars().first()

    if coach is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Such coach is not exist")

    db.delete(coach)
    db.commit()
    return


@router.delete("/news/{post_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["news endpoints"])
def remove_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Removes a post from news.
    """
    db_post = db.execute(
        select(News).where(News.id == post_id)
    ).scalars().first()

    if db_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Such coach is not exist")

    db.delete(db_post)
    db.commit()
    return
