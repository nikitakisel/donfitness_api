from datetime import datetime, timedelta
from decimal import Decimal
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


class ResidentCreate(BaseModel):
    user_id: int
    surname: str
    name: str
    birthdate: datetime
    email: str
    phone: str


class ResidentInfo(BaseModel):
    id: int
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
