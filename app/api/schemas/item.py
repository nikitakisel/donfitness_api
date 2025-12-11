from datetime import datetime, timedelta
from decimal import Decimal
from typing import Annotated, List, Dict
from pydantic import BaseModel, Field, validator, field_validator

from app.api.schemas.user import ResidentInfo


class NewsCreate(BaseModel):
    user_id: int
    post_title: str
    post_info: str
    post_image: str


class NewsUpdate(BaseModel):
    post_title: str | None = None
    post_info: str | None = None
    post_image: str | None = None


class CoachCreate(BaseModel):
    surname: str
    name: str
    speciality: str
    qualification: str
    extra_info: str


class CoachUpdate(BaseModel):
    surname: str | None = None
    name: str | None = None
    speciality: str | None = None
    qualification: str | None = None
    extra_info: str | None = None


class TrainingTypeCreate(BaseModel):
    training_name: str
    description: str


class AchievementCreate(BaseModel):
    achievement_name: str
    description: str
    criteria: str


class TrainingTypeUpdate(BaseModel):
    training_name: str | None = None
    description: str | None = None


class AchievementUpdate(BaseModel):
    achievement_name: str | None = None
    description: str | None = None
    criteria: str | None = None


class TrainingSessionCreate(BaseModel):
    training_type_id: int
    coach_id: int
    start_time: datetime
    duration: int
    max_capacity: int


class TrainingSessionUpdate(BaseModel):
    training_type_id: int | None = None
    coach_id: int | None = None
    start_time: datetime | None = None
    duration: int | None = None
    max_capacity: int | None = None


class ResidentToTrainingCreate(BaseModel):
    resident_id: int
    training_session_id: int


class ResidentToAchievementCreate(BaseModel):
    resident_id: int
    achievement_id: int


class NewsInfo(BaseModel):
    id: int
    username: str
    post_title: str
    post_info: str
    post_image: str
    post_time: datetime


class NewsUpdate(BaseModel):
    post_title: str | None = None
    post_info: str | None = None
    post_image: str | None = None
    post_time: datetime | None = None


class CoachInfo(BaseModel):
    id: int
    surname: str
    name: str
    speciality: str
    qualification: str
    extra_info: str


class TrainingTypeInfo(BaseModel):
    id: int
    training_name: str
    description: str


class AchievementInfo(BaseModel):
    id: int
    achievement_name: str
    description: str
    criteria: str


class TrainingTypeStatistics(BaseModel):
    training_name: str
    recorded_residents: int


class TrainingSessionInfo(BaseModel):
    id: int
    training_type: str
    coach_surname: str
    coach_name: str
    start_time: datetime
    duration: int
    remaining_places: int
    max_capacity: int


class TrainingSessionShortInfo(BaseModel):
    id: int
    training_type_id: int
    coach_id: int
    start_time: datetime
    duration: int
    max_capacity: int


class TrainingSessionInfoWithResidents(BaseModel):
    id: int
    training_type: str
    coach_surname: str
    coach_name: str
    start_time: datetime
    duration: int
    remaining_places: int
    max_capacity: int
    residents: List[ResidentInfo]
