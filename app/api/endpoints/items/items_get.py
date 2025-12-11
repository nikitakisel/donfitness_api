from datetime import datetime, timedelta
from typing import Annotated, List

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, select, ForeignKey, text, func
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship, backref

from app.api.endpoints.users import get_current_active_user
from app.api.repositories.get_training_session_data import fetch_training_session_data
from app.api.repositories.tournament_queries import TOURNAMENT_STANDINGS_SQL
from app.api.models.models import User, News, Resident, Coach, TrainingType, TrainingSession, ResidentToTraining, \
    Achievement, ResidentToAchievement
from app.api.schemas.item import NewsInfo, CoachInfo, TrainingSessionInfo, TrainingSessionInfoWithResidents, \
    TrainingTypeInfo, AchievementInfo, TrainingTypeStatistics
from app.api.schemas.user import ResidentInfo

from app.database import get_db

router = APIRouter()


@router.get("/news/all", response_model=List[NewsInfo], tags=["news endpoints"])
def get_all_news(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Retrieves information for all news.
    """
    news = db.execute(select(News).order_by(News.post_time)).scalars().all()
    news_data = []
    for new in news:
        news_data.append(NewsInfo(
            id=new.id,
            username=new.user.username,
            post_title=new.post_title,
            post_info=new.post_info,
            post_image=new.post_image,
            post_time=new.post_time,
        ))

    return news_data


@router.get("/news/{new_id}", response_model=NewsInfo, tags=["news endpoints"])
def get_new_by_id(new_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Retrieves information for current new.
    """
    new = db.execute(select(News).where(News.id == new_id)).scalars().first()

    if new is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="New not found")

    return NewsInfo(
        id=new.id,
        username=new.user.username,
        post_title=new.post_title,
        post_info=new.post_info,
        post_image=new.post_image,
        post_time=new.post_time,
    )


@router.get("/coaches/all", response_model=List[CoachInfo], tags=["coaches endpoints"])
def get_all_coaches(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Retrieves information for all coaches.
    """
    coaches = db.execute(select(Coach).order_by(Coach.surname, Coach.name)).scalars().all()
    return coaches


@router.get("/coaches/{coach_id}", response_model=CoachInfo, tags=["coaches endpoints"])
def read_coach(coach_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    coach = db.execute(select(Coach).where(Coach.id == coach_id)).scalars().first()
    if coach is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coach not found")
    return coach


@router.get("/training_sessions/all", response_model=List[TrainingSessionInfo], tags=["training sessions endpoints"])
def read_training_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    training_sessions_data = []
    training_sessions = db.execute(select(TrainingSession).order_by(TrainingSession.start_time)).scalars().all()
    for session in training_sessions:
        training_sessions_data.append(
            TrainingSessionInfo(
                id=session.id,
                training_type=session.training_type.training_name,
                coach_surname=session.coach.surname,
                coach_name=session.coach.name,
                start_time=session.start_time,
                duration=session.duration,
                remaining_places=session.remaining_places,
                max_capacity=session.max_capacity
            )
        )

    return training_sessions_data


@router.get("/training_sessions/enrolled", response_model=List[TrainingSessionInfo], tags=["resident panel"])
def read_enrolled_training_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Returns a list of training sessions the current user is enrolled in.
    """
    resident = db.execute(select(Resident).where(Resident.user_id == current_user.id)).scalars().first()
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found for this user")

    enrolled_sessions = sorted([
        ResidentToTraining.training_session
        for ResidentToTraining in resident.trainings
    ],
        key=lambda item: item.start_time
    )

    return fetch_training_session_data(enrolled_sessions)


@router.get("/training_sessions/not_enrolled", response_model=List[TrainingSessionInfo], tags=["resident panel"])
def read_not_enrolled_training_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Returns a list of training sessions the current user is NOT enrolled in.
    """
    resident = db.execute(select(Resident).where(Resident.user_id == current_user.id)).scalars().first()
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found for this user")

    # Get IDs of enrolled training sessions
    enrolled_session_ids = {
        training.training_session_id for training in resident.trainings
    }

    # Get all training sessions and filter out the enrolled ones
    all_sessions = db.execute(select(TrainingSession).order_by(TrainingSession.start_time)).scalars().all()
    not_enrolled_sessions = [
        session for session in all_sessions if session.id not in enrolled_session_ids
    ]
    return fetch_training_session_data(not_enrolled_sessions)


@router.get("/training_sessions/not_enrolled/{category_id}/{coach_id}", response_model=List[TrainingSessionInfo], tags=["resident panel"])
def read_not_enrolled_training_sessions_by_filter(category_id: int, coach_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Returns a list of training sessions the current user is NOT enrolled in BY filter.
    """
    resident = db.execute(select(Resident).where(Resident.user_id == current_user.id)).scalars().first()
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found for this user")

    # Get IDs of enrolled training sessions
    enrolled_session_ids = {
        training.training_session_id for training in resident.trainings
    }

    # Get all training sessions and filter out the enrolled ones
    if category_id > 0 and coach_id > 0:
        all_sessions = db.execute(
            select(TrainingSession).where(TrainingSession.training_type_id == category_id, TrainingSession.coach_id == coach_id).order_by(TrainingSession.start_time)).scalars().all()
    elif category_id > 0:
        all_sessions = db.execute(
            select(TrainingSession).where(TrainingSession.training_type_id == category_id).order_by(TrainingSession.start_time)).scalars().all()
    elif coach_id > 0:
        all_sessions = db.execute(
            select(TrainingSession).where(TrainingSession.coach_id == coach_id).order_by(TrainingSession.start_time)).scalars().all()
    else:
        all_sessions = db.execute(
            select(TrainingSession).order_by(TrainingSession.start_time)).scalars().all()

    not_enrolled_sessions = [
        session for session in all_sessions if session.id not in enrolled_session_ids
    ]
    return fetch_training_session_data(not_enrolled_sessions)


@router.get("/training_sessions/{training_session_id}", response_model=TrainingSessionInfo, tags=["training sessions endpoints"])
def read_training_session(training_session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    training_session = db.execute(select(TrainingSession).where(TrainingSession.id == training_session_id)).scalars().first()

    if training_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training session not found")

    return TrainingSessionInfo(
        id=training_session.id,
        training_type=training_session.training_type.training_name,
        coach_surname=training_session.coach.surname,
        coach_name=training_session.coach.name,
        start_time=training_session.start_time,
        duration=training_session.duration,
        remaining_places=training_session.remaining_places,
        max_capacity=training_session.max_capacity
    )


@router.get("/training_sessions/residents/{category_id}/{coach_id}/{resident_id}", response_model=List[TrainingSessionInfoWithResidents], tags=["training sessions endpoints"])
def read_training_sessions_with_residents(category_id: int, coach_id: int, resident_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Retrieves all training sessions with a list of residents enrolled in each session.
    """
    training_sessions_data = []
    if category_id > 0 and coach_id > 0:
        training_sessions = db.execute(
            select(TrainingSession).where(TrainingSession.training_type_id == category_id, TrainingSession.coach_id == coach_id).order_by(TrainingSession.start_time)).scalars().all()
    elif category_id > 0:
        training_sessions = db.execute(
            select(TrainingSession).where(TrainingSession.training_type_id == category_id).order_by(TrainingSession.start_time)).scalars().all()
    elif coach_id > 0:
        training_sessions = db.execute(
            select(TrainingSession).where(TrainingSession.coach_id == coach_id).order_by(TrainingSession.start_time)).scalars().all()
    else:
        training_sessions = db.execute(
            select(TrainingSession).order_by(TrainingSession.start_time)).scalars().all()

    for session in training_sessions:
        residents = db.execute(
            select(Resident)
            .join(ResidentToTraining, Resident.id == ResidentToTraining.resident_id)
            .where(ResidentToTraining.training_session_id == session.id)
        ).scalars().all()

        if resident_id == 0:
            residents_data = [ResidentInfo(
                id=resident.id,
                surname=resident.surname,
                name=resident.name,
                birthdate=resident.birthdate,
                email=resident.email,
                phone=resident.phone
            ) for resident in residents]

            training_sessions_data.append(
                TrainingSessionInfoWithResidents(
                    id=session.id,
                    training_type=session.training_type.training_name,
                    coach_surname=session.coach.surname,
                    coach_name=session.coach.name,
                    start_time=session.start_time,
                    duration=session.duration,
                    remaining_places=session.remaining_places,
                    max_capacity=session.max_capacity,
                    residents=residents_data
                )
            )

        else:
            residents_data = [ResidentInfo(
                id=resident.id,
                surname=resident.surname,
                name=resident.name,
                birthdate=resident.birthdate,
                email=resident.email,
                phone=resident.phone
            ) for resident in residents if resident.id == resident_id]

            if residents_data:
                training_sessions_data.append(
                    TrainingSessionInfoWithResidents(
                        id=session.id,
                        training_type=session.training_type.training_name,
                        coach_surname=session.coach.surname,
                        coach_name=session.coach.name,
                        start_time=session.start_time,
                        duration=session.duration,
                        remaining_places=session.remaining_places,
                        max_capacity=session.max_capacity,
                        residents=residents_data
                    )
                )

    return training_sessions_data


@router.get("/training_types/all", response_model=List[TrainingTypeInfo], tags=["resident panel", "training types endpoints"])
def read_training_types(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    training_types = db.execute(select(TrainingType).order_by(TrainingType.training_name)).scalars().all()
    return training_types


@router.get("/achievements/all", response_model=List[AchievementInfo], tags=["resident panel", "achievements endpoints"])
def read_achievements(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    achievements = db.execute(select(Achievement).order_by(Achievement.achievement_name)).scalars().all()
    return achievements


@router.get("/training_types/statistics", response_model=List[TrainingTypeStatistics], tags=["resident panel", "training types endpoints"])
def read_training_types_statistics(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_training_types_statistics = db.execute(select(
            TrainingType.training_name.label("training_name"),
            func.count().label("recorded_residents")
        )
        .join(TrainingSession, TrainingSession.training_type_id == TrainingType.id)
        .join(ResidentToTraining, ResidentToTraining.training_session_id == TrainingSession.id)
        .group_by(TrainingType.training_name)).all()

    return db_training_types_statistics


@router.get("/training_types/{type_id}", response_model=TrainingTypeInfo, tags=["training types endpoints"])
def read_training_type(type_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    training_type = db.execute(select(TrainingType).where(TrainingType.id == type_id)).scalars().first()

    if training_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training type not found")

    return training_type


@router.get("/achievements/received", response_model=List[AchievementInfo], tags=["achievements endpoints"])
def read_received_achievements(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Returns a list of achievements the current user is received.
    """
    resident = db.execute(select(Resident).where(Resident.user_id == current_user.id)).scalars().first()
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found for this user")

    received_achievements = sorted([
        ResidentToAchievement.achievement
        for ResidentToAchievement in resident.achievements
    ],
        key=lambda item: item.achievement_name
    )

    return received_achievements


@router.get("/achievements/not_received", response_model=List[AchievementInfo], tags=["achievements endpoints"])
def read_not_received_achievements(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Returns a list of achievements the current user is NOT received.
    """
    resident = db.execute(select(Resident).where(Resident.user_id == current_user.id)).scalars().first()
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found for this user")

    received_achievements_ids = {
        achievement.achievement_id for achievement in resident.achievements
    }

    all_achievements = db.execute(select(Achievement).order_by(Achievement.achievement_name)).scalars().all()
    not_received_achievements = [
        achievement for achievement in all_achievements if achievement.id not in received_achievements_ids
    ]
    return not_received_achievements


@router.get("/achievements/{achievement_id}", response_model=AchievementInfo, tags=["achievements endpoints"])
def read_achievement(achievement_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    achievement = db.execute(select(Achievement).where(Achievement.id == achievement_id)).scalars().first()

    if achievement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Achievement not found")

    return achievement
