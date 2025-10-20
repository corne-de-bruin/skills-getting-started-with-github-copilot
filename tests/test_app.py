import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    # Test if we get a dictionary
    assert isinstance(activities, dict)
    
    # Test if activities have the required fields
    for activity_name, details in activities.items():
        assert isinstance(activity_name, str)
        assert isinstance(details, dict)
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)

def test_signup_for_activity():
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    
    # First, try to sign up
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    
    # Verify the participant was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]
    
    # Try to sign up again (should fail)
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_unregister_from_activity():
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    
    # First, make sure the user is signed up (using the signup endpoint)
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Now try to unregister
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    
    # Verify the participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]
    
    # Try to unregister again (should fail)
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]

def test_signup_nonexistent_activity():
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_unregister_nonexistent_activity():
    response = client.delete("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]