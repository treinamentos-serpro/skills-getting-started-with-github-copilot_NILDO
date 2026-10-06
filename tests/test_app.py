import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_signup_adds_student_to_activity():
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 200
    assert "student@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_student():
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_signup_rejects_unknown_activity():
    response = client.post(
        "/activities/Unknown/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404


def test_cancel_signup_removes_student():
    email = "student@mergington.edu"
    activities["Chess Club"]["participants"].append(email)

    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_cancel_signup_rejects_unregistered_student():
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
