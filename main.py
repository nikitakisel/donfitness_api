from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, select, ForeignKey, func
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship, backref
from datetime import datetime, timedelta
from typing import Annotated, List, Dict
import bcrypt
import jwt
from pydantic import BaseModel, Field, validator, field_validator
from models import *

# Database Configuration (Replace with your actual database URL)
DATABASE_URL = "postgresql://postgres:postpass@localhost:5432/donfitness"
SECRET_KEY = "L724SF7qpmGRDRVifUDXIn5wogaA4VxQHZYNgnbo9begeW5373"  # Replace with a strong, random secret key!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120


# Models
# Moved to "models"


# SQLAlchemy Engine and Session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(engine)

# FastAPI App
app = FastAPI()

# Security Dependencies
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

origins = [
   "http://localhost:3000",  # The origin of your React app
   "http://localhost:8000",  # Maybe allow the backend itself
   # Add other origins as needed (e.g., for production)
]

app.add_middleware(
   CORSMiddleware,
   allow_origins=origins,
   allow_credentials=True,  # Important for cookies and sessions
   allow_methods=["*"],      # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
   allow_headers=["*"],      # Allows all headers in the request
)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency to get current active user
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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


# Pydantic Models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=4, max_length=30)  # Example validation
    password: str = Field(..., min_length=8)  # Example validation
    surname: str
    name: str
    birthdate: datetime  # Use datetime (Python's datetime)
    email: str
    phone: str

    @field_validator('birthdate')  # Use field_validator and specify the field name
    def parse_dates(cls, value: datetime):
        if isinstance(value, datetime):  # Check if it's already a datetime object
            return value
        try:
            return datetime.fromisoformat(value.rstrip('Z'))  # Attempt ISO format parsing
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
            return None  # Allow null values
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


# Pydantic model for ResidentToTraining
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
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Authentication Function
def authenticate_user(db: Session, username: str, password: str):
    user = db.execute(select(User).where(User.username == username)).scalars().first()
    if not user:
        return None
    if bcrypt.checkpw(password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        return user
    return None


# Fetch training session data
def fetch_training_session_data(training_sessions: List[TrainingSession]):
    training_sessions_data = []
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


# API Endpoints
# Auth Endpoints
@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["account managing"])
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


@app.post("/token", response_model=Token, tags=["account managing"])
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserResponse, tags=["resident panel"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/news/all", response_model=List[NewsInfo], tags=["news endpoints"])
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


@app.get("/news/{new_id}", response_model=NewsInfo, tags=["news endpoints"])
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


@app.get("/coaches/all", response_model=List[CoachInfo], tags=["coaches endpoints"])
def get_all_coaches(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Retrieves information for all coaches.
    """
    coaches = db.execute(select(Coach).order_by(Coach.surname)).scalars().all()
    return coaches


# POST Endpoints for Models (Protected)
@app.post("/residents/", response_model=ResidentInfo, status_code=status.HTTP_201_CREATED, tags=["account managing"])
def create_resident(resident: ResidentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_resident = Resident(**resident.dict())
    db.add(db_resident)
    db.commit()
    db.refresh(db_resident)
    return db_resident


@app.post("/news/", response_model=None, status_code=status.HTTP_201_CREATED, tags=["news endpoints"])
def create_post(news: NewsCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_news = News(**news.dict())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news


@app.post("/coaches/", response_model=CoachInfo, status_code=status.HTTP_201_CREATED, tags=["coaches endpoints"])
def create_coach(coach: CoachCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_coach = Coach(**coach.dict())
    db.add(db_coach)
    db.commit()
    db.refresh(db_coach)
    return db_coach


@app.post("/training_types/", response_model=None, status_code=status.HTTP_201_CREATED, tags=["training types endpoints"])
def create_training_type(training_type: TrainingTypeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_training_type = TrainingType(**training_type.dict())
    db.add(db_training_type)
    db.commit()
    db.refresh(db_training_type)
    return db_training_type


@app.post("/training_sessions/", response_model=None, status_code=status.HTTP_201_CREATED, tags=["training sessions endpoints"])
def create_training_session(training_session: TrainingSessionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_training_session = TrainingSession(**training_session.dict())
    db.add(db_training_session)
    db.commit()
    db.refresh(db_training_session)
    return db_training_session


# POST Endpoint for Resident to Training (Protected)
@app.post("/resident_to_training/", status_code=status.HTTP_201_CREATED, tags=["resident panel"])
def add_resident_to_training(resident_to_training: ResidentToTrainingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_resident_to_training = ResidentToTraining(**resident_to_training.dict())
    db.add(db_resident_to_training)
    db.commit()
    return {"message": "Resident added to training successfully"}


# GET Endpoints for Information (Protected)
@app.get("/residents/{resident_id}", response_model=ResidentInfo, tags=["resident panel"])
def read_resident(resident_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    resident = db.execute(select(Resident).where(Resident.id == resident_id)).scalars().first()
    if resident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")
    return resident


@app.get("/coaches/{coach_id}", response_model=CoachInfo, tags=["coaches endpoints"])
def read_coach(coach_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    coach = db.execute(select(Coach).where(Coach.id == coach_id)).scalars().first()
    if coach is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coach not found")
    return coach


@app.get("/training_sessions/all", response_model=List[TrainingSessionInfo], tags=["training sessions endpoints"])
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


@app.get("/training_sessions/enrolled", response_model=List[TrainingSessionInfo], tags=["resident panel"])
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


@app.get("/training_sessions/not_enrolled", response_model=List[TrainingSessionInfo], tags=["resident panel"])
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


@app.get("/training_sessions/not_enrolled/{category_id}/{coach_id}", response_model=List[TrainingSessionInfo], tags=["resident panel"])
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


@app.get("/training_sessions/{training_session_id}", response_model=TrainingSessionInfo, tags=["training sessions endpoints"])
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


@app.get("/training_sessions/residents/{category_id}/{coach_id}", response_model=List[TrainingSessionInfoWithResidents], tags=["training sessions endpoints"])
def read_training_sessions_with_residents(category_id: int, coach_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
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

    return training_sessions_data


@app.get("/training_types/all", response_model=List[TrainingTypeInfo], tags=["resident panel", "training types endpoints"])
def read_training_types(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    training_types_data = []
    training_types = db.execute(select(TrainingType).order_by(TrainingType.training_name)).scalars().all()
    for training_type in training_types:
        training_types_data.append(
            TrainingTypeInfo(
                id=training_type.id,
                training_name=training_type.training_name,
                description=training_type.description
            )
        )

    return training_types_data


@app.get("/training_types/{type_id}", response_model=TrainingTypeInfo, tags=["training types endpoints"])
def read_training_type(type_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    training_type = db.execute(select(TrainingType).where(TrainingType.id == type_id)).scalars().first()

    if training_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training type not found")

    return TrainingTypeInfo(
        id=training_type.id,
        training_name=training_type.training_name,
        description=training_type.description
    )


# PUT Endpoints (Protected)
@app.put("/residents/{resident_id}", response_model=ResidentInfo, tags=["resident panel"])
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


@app.put("/training_sessions/{session_id}", response_model=TrainingSessionShortInfo, tags=["training sessions endpoints"])
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


@app.put("/training_types/{type_id}", response_model=TrainingTypeInfo, tags=["training types endpoints"])
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


@app.put("/coaches/{coach_id}", response_model=CoachInfo, tags=["coaches endpoints"])
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


@app.put("/news/{news_id}", response_model=NewsInfo, tags=["news endpoints"])
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


# DELETE Endpoints (Protected)
@app.delete("/resident_to_training/{resident_id}/{training_session_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["resident panel", "training sessions endpoints"])
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


@app.delete("/training_sessions/{training_session_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["training sessions endpoints"])
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


@app.delete("/training_types/{type_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["training types endpoints"])
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


@app.delete("/coaches/{coach_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["coaches endpoints"])
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


@app.delete("/news/{post_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["news endpoints"])
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


@app.delete("/coaches/{coach_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["coaches endpoints"])
def remove_coach(coach_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Removes a coach.
    """
    db_coach = db.execute(select(Coach).where(Coach.id == coach_id)).scalars().first()

    if db_coach is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Such coach is not exist")

    db.delete(db_coach)
    db.commit()
    return


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
