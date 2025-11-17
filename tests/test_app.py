import copy
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def setup_function(function):
    # snapshot activities so tests don't leak state
    global _activities_backup
    _activities_backup = copy.deepcopy(activities)


def teardown_function(function):
    # restore original activities
    activities.clear()
    activities.update(copy.deepcopy(_activities_backup))


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert "Chess Club" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "testuser@example.com"

    # initial count
    initial = len(activities[activity]["participants"])

    # signup
    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 200
    assert "Signed up" in res.json().get("message", "")

    # verify added
    res2 = client.get("/activities")
    assert email in res2.json()[activity]["participants"]
    assert len(res2.json()[activity]["participants"]) == initial + 1

    # unregister
    res3 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert res3.status_code == 200
    assert "Unregistered" in res3.json().get("message", "")

    # verify removed and count back to initial
    res4 = client.get("/activities")
    assert email not in res4.json()[activity]["participants"]
    assert len(res4.json()[activity]["participants"]) == initial
