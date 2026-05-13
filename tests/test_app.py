from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
initial_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities state before each test."""
    activities.clear()
    activities.update(deepcopy(initial_activities))
    yield


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activities = deepcopy(initial_activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "oliver@mergington.edu"
    assert new_email not in activities[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={new_email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Programming Class"
    existing_email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={existing_email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_success():
    # Arrange
    activity_name = "Gym Class"
    existing_email = activities[activity_name]["participants"][0]
    assert existing_email in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={existing_email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {existing_email} from {activity_name}"}
    assert existing_email not in activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_400():
    # Arrange
    activity_name = "Art Club"
    missing_email = "missing@mergington.edu"
    assert missing_email not in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={missing_email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Participant not found"


def test_unknown_activity_returns_404_for_signup():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unknown_activity_returns_404_for_delete():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
