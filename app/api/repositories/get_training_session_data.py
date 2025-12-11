from typing import List

from app.api.models.models import TrainingSession
from app.api.schemas.item import TrainingSessionInfo


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
