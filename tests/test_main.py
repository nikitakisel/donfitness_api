import pytest
from datetime import datetime, timedelta
from main import User, Resident, News, Coach, TrainingType, TrainingSession, ResidentToTraining
from main import get_current_user, get_current_active_user

def test_register_user_success(client, test_user_data, db_session):
    response = client.post("/register", json=test_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == test_user_data["username"]
    assert "id" in data
    assert data["is_active"] is True

    # Verify resident was also created
    resident = db_session.query(Resident).filter(Resident.user_id == data["id"]).first()
    assert resident is not None
    assert resident.email == test_user_data["email"]

def test_register_user_duplicate_username(client, test_user, test_user_data):
    # Try to register the same user again
    response = client.post("/register", json=test_user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"

def test_login_success(client, test_user, test_user_data):
    response = client.post(
        "/token",
        data={"username": test_user_data["username"], "password": test_user_data["password"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client, test_user_data):
    response = client.post(
        "/token",
        data={"username": test_user_data["username"], "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_read_users_me_success(authenticated_client, test_user):
    response = authenticated_client.get("/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user.username
    assert data["id"] == test_user.id
    assert data["is_active"] is True

def test_read_users_me_unauthorized(client):
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# Тесты для новостей
def test_create_news_success(authenticated_client, test_user):
    news_data = {
        "user_id": test_user.id,
        "post_title": "New Event",
        "post_info": "Come join us for a fun event!",
        "post_image": "http://example.com/new_event.jpg"
    }
    response = authenticated_client.post("/news/", json=news_data)
    assert response.status_code == 201

def test_get_all_news_success(authenticated_client, test_news):
    response = authenticated_client.get("/news/all")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["post_title"] == test_news.post_title

def test_get_news_by_id_success(authenticated_client, test_news):
    response = authenticated_client.get(f"/news/{test_news.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["post_title"] == test_news.post_title
    assert data["username"] == test_news.user.username

def test_get_news_by_id_not_found(authenticated_client):
    response = authenticated_client.get("/news/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "New not found"

def test_update_news_success(authenticated_client, test_news):
    updated_data = {
        "post_title": "Updated News Title",
        "post_info": "This news has been updated.",
    }
    response = authenticated_client.put(f"/news/{test_news.id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["post_title"] == updated_data["post_title"]
    assert data["post_info"] == updated_data["post_info"]
    assert data["id"] == test_news.id

def test_delete_news_success(authenticated_client, test_news, db_session):
    response = authenticated_client.delete(f"/news/{test_news.id}")
    assert response.status_code == 204
    # Verify it's deleted
    deleted_news = db_session.query(News).filter(News.id == test_news.id).first()
    assert deleted_news is None

def test_delete_news_not_found(authenticated_client):
    response = authenticated_client.delete("/news/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Such coach is not exist" # Typo in original code, should be "News post not found"

# Тесты для тренеров
def test_create_coach_success(authenticated_client):
    coach_data = {
        "surname": "Doe",
        "name": "Jane",
        "speciality": "Cardio",
        "qualification": "Level 2",
        "extra_info": "Loves running"
    }
    response = authenticated_client.post("/coaches/", json=coach_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == coach_data["name"]

def test_get_all_coaches_success(authenticated_client, test_coach):
    response = authenticated_client.get("/coaches/all")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == test_coach.name

def test_get_coach_by_id_success(authenticated_client, test_coach):
    response = authenticated_client.get(f"/coaches/{test_coach.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_coach.name

def test_update_coach_success(authenticated_client, test_coach):
    updated_data = {
        "speciality": "Weightlifting",
        "extra_info": "Certified powerlifter"
    }
    response = authenticated_client.put(f"/coaches/{test_coach.id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["speciality"] == updated_data["speciality"]
    assert data["extra_info"] == updated_data["extra_info"]

def test_delete_coach_success(authenticated_client, test_coach, db_session):
    response = authenticated_client.delete(f"/coaches/{test_coach.id}")
    assert response.status_code == 204
    deleted_coach = db_session.query(Coach).filter(Coach.id == test_coach.id).first()
    assert deleted_coach is None

# Тесты для типов тренировок
def test_create_training_type_success(authenticated_client):
    ttype_data = {
        "training_name": "Pilates",
        "description": "Core strength"
    }
    response = authenticated_client.post("/training_types/", json=ttype_data)
    assert response.status_code == 201

def test_get_training_type_by_id_success(authenticated_client, test_training_type):
    response = authenticated_client.get(f"/training_types/{test_training_type.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["training_name"] == test_training_type.training_name

def test_update_training_type_success(authenticated_client, test_training_type):
    updated_data = {
        "description": "Advanced core strength and flexibility"
    }
    response = authenticated_client.put(f"/training_types/{test_training_type.id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == updated_data["description"]

def test_delete_training_type_success(authenticated_client, test_training_type, db_session):
    response = authenticated_client.delete(f"/training_types/{test_training_type.id}")
    assert response.status_code == 204
    deleted_type = db_session.query(TrainingType).filter(TrainingType.id == test_training_type.id).first()
    assert deleted_type is None

# Тесты для тренировочных сессий
def test_create_training_session_success(authenticated_client, test_coach, test_training_type):
    session_data = {
        "training_type_id": test_training_type.id,
        "coach_id": test_coach.id,
        "start_time": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "duration": 90,
        "max_capacity": 15
    }
    response = authenticated_client.post("/training_sessions/", json=session_data)
    assert response.status_code == 201

def test_get_all_training_sessions_success(authenticated_client, test_training_session):
    response = authenticated_client.get("/training_sessions/all")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["id"] == test_training_session.id
    assert data[0]["training_type"] == test_training_session.training_type.training_name

def test_get_training_session_by_id_success(authenticated_client, test_training_session):
    response = authenticated_client.get(f"/training_sessions/{test_training_session.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_training_session.id
    assert data["coach_surname"] == test_training_session.coach.surname

def test_update_training_session_success(authenticated_client, test_training_session):
    updated_data = {
        "duration": 75,
        "max_capacity": 12
    }
    response = authenticated_client.put(f"/training_sessions/{test_training_session.id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["duration"] == updated_data["duration"]
    assert data["max_capacity"] == updated_data["max_capacity"]

def test_delete_training_session_success(authenticated_client, test_training_session, db_session):
    response = authenticated_client.delete(f"/training_sessions/{test_training_session.id}")
    assert response.status_code == 204
    deleted_session = db_session.query(TrainingSession).filter(TrainingSession.id == test_training_session.id).first()
    assert deleted_session is None

def test_read_enrolled_training_sessions_success(authenticated_client, test_user, test_training_session, db_session):
    resident = db_session.query(Resident).filter(Resident.user_id == test_user.id).first()
    enrollment = ResidentToTraining(resident_id=resident.id, training_session_id=test_training_session.id)
    db_session.add(enrollment)
    db_session.commit()

    response = authenticated_client.get("/training_sessions/enrolled")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["id"] == test_training_session.id

def test_read_not_enrolled_training_sessions_with_filters(authenticated_client, test_user, test_training_session, db_session):
    # Ensure test_training_session is not enrolled
    resident = db_session.query(Resident).filter(Resident.user_id == test_user.id).first()
    db_session.query(ResidentToTraining).filter(
        ResidentToTraining.resident_id == resident.id,
        ResidentToTraining.training_session_id == test_training_session.id
    ).delete()
    db_session.commit()

    # Filter by training type
    response = authenticated_client.get(f"/training_sessions/not_enrolled/{test_training_session.training_type.id}/0")
    assert response.status_code == 200
    data = response.json()
    assert any(s["id"] == test_training_session.id for s in data)

    # Filter by coach
    response = authenticated_client.get(f"/training_sessions/not_enrolled/0/{test_training_session.coach.id}")
    assert response.status_code == 200
    data = response.json()
    assert any(s["id"] == test_training_session.id for s in data)

    # Filter by both
    response = authenticated_client.get(f"/training_sessions/not_enrolled/{test_training_session.training_type.id}/{test_training_session.coach.id}")
    assert response.status_code == 200
    data = response.json()
    assert any(s["id"] == test_training_session.id for s in data)

def test_remove_resident_from_training_not_enrolled(authenticated_client, test_user, test_training_session, db_session):
    resident = db_session.query(Resident).filter(Resident.user_id == test_user.id).first()
    response = authenticated_client.delete(f"/resident_to_training/{resident.id}/{test_training_session.id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Resident is not enrolled in this training session"

def test_read_training_sessions_with_residents_success(authenticated_client, test_user, test_training_session, db_session):
    resident = db_session.query(Resident).filter(Resident.user_id == test_user.id).first()
    enrollment = ResidentToTraining(resident_id=resident.id, training_session_id=test_training_session.id)
    db_session.add(enrollment)
    db_session.commit()

    response = authenticated_client.get(f"/training_sessions/residents/0/0/0") # No filters
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    session_data = next((s for s in data if s["id"] == test_training_session.id), None)
    assert session_data is not None
    assert len(session_data["residents"]) == 1
    assert session_data["residents"][0]["id"] == resident.id

def test_read_training_sessions_with_residents_filtered_by_resident_id(authenticated_client, test_user, another_test_user, test_training_session, db_session):
    resident1 = db_session.query(Resident).filter(Resident.user_id == test_user.id).first()
    resident2 = db_session.query(Resident).filter(Resident.user_id == another_test_user.id).first()

    enrollment1 = ResidentToTraining(resident_id=resident1.id, training_session_id=test_training_session.id)
    enrollment2 = ResidentToTraining(resident_id=resident2.id, training_session_id=test_training_session.id)
    db_session.add_all([enrollment1, enrollment2])
    db_session.commit()

    # Filter for resident1
    response = authenticated_client.get(f"/training_sessions/residents/0/0/{resident1.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1 # Only one session should be returned
    assert data[0]["id"] == test_training_session.id
    assert len(data[0]["residents"]) == 1
    assert data[0]["residents"][0]["id"] == resident1.id

    # Filter for resident2
    response = authenticated_client.get(f"/training_sessions/residents/0/0/{resident2.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == test_training_session.id
    assert len(data[0]["residents"]) == 1
    assert data[0]["residents"][0]["id"] == resident2.id

    # Filter for non-existent resident
    response = authenticated_client.get(f"/training_sessions/residents/0/0/9999")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
