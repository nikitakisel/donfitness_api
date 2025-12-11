from sqlalchemy.orm import Session, declarative_base

from app.config import engine, oauth2_scheme, settings, SessionLocal

Base = declarative_base()
# Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
