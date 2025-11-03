import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# Импортируем все из вашего основного файла приложения
# Предполагается, что ваш код находится в файле `main.py`
from main import app, get_db, Base, User, Resident, News, Coach, TrainingType, TrainingSession, ResidentToTraining, hash_password, create_access_token, ALGORITHM, SECRET_KEY
from main import get_current_user, get_current_active_user # Импортируем зависимости

# Используем in-memory SQLite для тестов
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:" # Можно использовать полностью in-memory для еще большей изоляции

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """Provides a database engine for the entire test session."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine) # Очищаем базу после всех тестов

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Provides a clean database session for each test function."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Override the get_db dependency for tests
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield session

    session.close()
    transaction.rollback() # Откатываем все изменения после каждого теста
    connection.close()
    app.dependency_overrides.clear() # Очищаем переопределения зависимостей

@pytest.fixture(scope="function")
def client(db_session):
    """Provides a TestClient for making requests to the FastAPI app."""
    return TestClient(app)

@pytest.fixture(scope="function")
def test_user_data():
    """Returns data for a test user."""
    return {
        "username": "testuser",
        "password": "testpassword",
        "surname": "Test",
        "name": "User",
        "birthdate": datetime(1990, 1, 1).isoformat(),
        "email": "test@example.com",
        "phone": "1234567890"
    }

@pytest.fixture(scope="function")
def another_test_user_data():
    """Returns data for another test user."""
    return {
        "username": "anotheruser",
        "password": "anotherpassword",
        "surname": "Another",
        "name": "User",
        "birthdate": datetime(1992, 2, 2).isoformat(),
        "email": "another@example.com",
        "phone": "0987654321"
    }

@pytest.fixture(scope="function")
def test_user(db_session, test_user_data):
    """Creates and returns a test user in the database."""
    hashed_password = hash_password(test_user_data["password"])
    user = User(username=test_user_data["username"], hashed_password=hashed_password, is_active=True)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    resident = Resident(
        user_id=user.id,
        surname=test_user_data["surname"],
        name=test_user_data["name"],
        birthdate=datetime.fromisoformat(test_user_data["birthdate"]),
        email=test_user_data["email"],
        phone=test_user_data["phone"]
    )
    db_session.add(resident)
    db_session.commit()
    db_session.refresh(resident)
    return user

@pytest.fixture(scope="function")
def another_test_user(db_session, another_test_user_data):
    """Creates and returns another test user in the database."""
    hashed_password = hash_password(another_test_user_data["password"])
    user = User(username=another_test_user_data["username"], hashed_password=hashed_password, is_active=True)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    resident = Resident(
        user_id=user.id,
        surname=another_test_user_data["surname"],
        name=another_test_user_data["name"],
        birthdate=datetime.fromisoformat(another_test_user_data["birthdate"]),
        email=another_test_user_data["email"],
        phone=another_test_user_data["phone"]
    )
    db_session.add(resident)
    db_session.commit()
    db_session.refresh(resident)
    return user

@pytest.fixture(scope="function")
def auth_token(test_user):
    """Generates an access token for the test user."""
    access_token_expires = timedelta(minutes=30)
    return create_access_token(data={"sub": test_user.username}, expires_delta=access_token_expires)

@pytest.fixture(scope="function")
def authenticated_client(client, test_user):
    """Provides a TestClient with an authenticated test user."""
    # Override get_current_user and get_current_active_user to return our test_user directly
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_current_active_user] = lambda: test_user
    yield client
    app.dependency_overrides.clear() # Clear overrides after the test

@pytest.fixture(scope="function")
def test_coach(db_session):
    """Creates and returns a test coach."""
    coach = Coach(surname="Coach", name="John", speciality="Fitness", qualification="Certified", extra_info="Experienced")
    db_session.add(coach)
    db_session.commit()
    db_session.refresh(coach)
    return coach

@pytest.fixture(scope="function")
def test_training_type(db_session):
    """Creates and returns a test training type."""
    ttype = TrainingType(training_name="Yoga", description="Relaxing session")
    db_session.add(ttype)
    db_session.commit()
    db_session.refresh(ttype)
    return ttype

@pytest.fixture(scope="function")
def test_training_session(db_session, test_coach, test_training_type):
    """Creates and returns a test training session."""
    session = TrainingSession(
        training_type_id=test_training_type.id,
        coach_id=test_coach.id,
        start_time=datetime.utcnow() + timedelta(days=1),
        duration=60,
        max_capacity=10
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session

@pytest.fixture(scope="function")
def test_news(db_session, test_user):
    """Creates and returns a test news post."""
    news = News(
        user_id=test_user.id,
        post_title="Test News Title",
        post_info="This is a test news post.",
        post_image="http://example.com/image.jpg",
        post_time=datetime.utcnow()
    )
    db_session.add(news)
    db_session.commit()
    db_session.refresh(news)
    return news
