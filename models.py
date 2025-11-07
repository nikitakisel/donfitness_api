from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, select, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship, backref
from datetime import datetime

# SQLAlchemy Setup
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    resident = relationship("Resident", back_populates="user", uselist=False, cascade="all, delete-orphan")
    news = relationship("News", back_populates="user", cascade="all, delete-orphan")


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    post_title = Column(String)
    post_info = Column(Text)
    post_image = Column(Text)
    post_time = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="news")


class Resident(Base):
    __tablename__ = "residents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    surname = Column(String)
    name = Column(String)
    birthdate = Column(DateTime)
    email = Column(String)
    phone = Column(String)

    user = relationship("User", back_populates="resident")
    trainings = relationship("ResidentToTraining", back_populates="resident", cascade="all, delete-orphan")


class Coach(Base):
    __tablename__ = "coaches"

    id = Column(Integer, primary_key=True, index=True)
    surname = Column(String)
    name = Column(String)
    speciality = Column(Text)
    qualification = Column(Text)
    extra_info = Column(Text)

    training_sessions = relationship("TrainingSession", back_populates="coach", cascade="all, delete-orphan")


class TrainingType(Base):
    __tablename__ = "training_types"
    id = Column(Integer, primary_key=True, index=True)
    training_name = Column(String)
    description = Column(Text)

    training_sessions = relationship("TrainingSession", back_populates="training_type", cascade="all, delete-orphan")


class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True, index=True)
    training_type_id = Column(Integer, ForeignKey("training_types.id", ondelete="CASCADE"), index=True)
    coach_id = Column(Integer, ForeignKey("coaches.id", ondelete="CASCADE"), index=True)
    start_time = Column(DateTime)
    duration = Column(Integer)
    max_capacity = Column(Integer)

    residents = relationship("ResidentToTraining", back_populates="training_session", cascade="all, delete-orphan")
    training_type = relationship("TrainingType", back_populates="training_sessions")
    coach = relationship("Coach", back_populates="training_sessions")

    @property
    def remaining_places(self):
        return self.max_capacity - len(self.residents)


class ResidentToTraining(Base):
    __tablename__ = "residents_to_trainings"

    id = Column(Integer, primary_key=True, index=True)
    resident_id = Column(Integer, ForeignKey("residents.id", ondelete="CASCADE"), index=True)
    training_session_id = Column(Integer, ForeignKey("training_sessions.id", ondelete="CASCADE"), index=True)

    resident = relationship("Resident", back_populates="trainings")
    training_session = relationship("TrainingSession", back_populates="residents")
