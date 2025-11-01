from datetime import datetime, timedelta
from typing import Annotated, List, Dict
from pydantic import BaseModel, Field, validator, field_validator


class UserCreate(BaseModel):
    username: str = Field(..., min_length=4, max_length=30)
    password: str = Field(..., min_length=8)
    surname: str
    name: str
    birthdate: datetime
    email: str
    phone: str

    @field_validator('birthdate')
    def parse_dates(cls, value: datetime):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value.rstrip('Z'))
        except ValueError:
            raise ValueError('Invalid datetime format.  Should be ISO 8601 format.')


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    username: str
    is_active: bool


class NewsCreate(BaseModel):
    user_id: int
    post_title: str
    post_info: str
    post_image: str


class NewsUpdate(BaseModel):
    post_title: str | None = None
    post_info: str | None = None
    post_image: str | None = None


class ResidentCreate(BaseModel):
    user_id: int
    surname: str
    name: str
    birthdate: datetime
    email: str
    phone: str


class ResidentUpdate(BaseModel):
    surname: str | None = None
    name: str | None = None
    birthdate: datetime | None = None
    email: str | None = None
    phone: str | None = None

    @field_validator('birthdate')
    def parse_dates(cls, value: datetime | None):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value.rstrip('Z'))
        except ValueError:
            raise ValueError('Invalid datetime format.  Should be ISO 8601 format.')


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


class TrainingTypeUpdate(BaseModel):
    training_name: str | None = None
    description: str | None = None


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


class ResidentInfo(BaseModel):
    id: int
    surname: str
    name: str
    birthdate: datetime
    email: str
    phone: str


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
