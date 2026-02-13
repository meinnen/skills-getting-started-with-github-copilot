import pytest
from fastapi.testclient import TestClient


class TestActivities:
    """Tests for the activities endpoints"""

    def test_get_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that we get at least some activities
        assert len(data) > 0
        
        # Check that each activity has the required fields
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data

    def test_get_activities_contains_expected_activities(self, client):
        """Test that expected activities are in the response"""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = ["Basketball", "Tennis Club", "Art Club", "Music Ensemble"]
        for activity in expected_activities:
            assert activity in data

    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/NonexistentClub/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_already_registered(self, client):
        """Test that a student can't sign up twice for the same activity"""
        email = "unique.student@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            "/activities/Basketball/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            "/activities/Basketball/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"].lower()

    def test_unregister_from_activity_success(self, client):
        """Test successful unregistration from an activity"""
        email = "test.unregister@mergington.edu"
        
        # First, sign up
        signup_response = client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Then unregister
        unregister_response = client.delete(
            "/activities/Tennis Club/unregister",
            params={"email": email}
        )
        
        assert unregister_response.status_code == 200
        data = unregister_response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from an activity that doesn't exist"""
        response = client.delete(
            "/activities/NonexistentClub/unregister",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404

    def test_unregister_not_registered(self, client):
        """Test unregister when student is not registered"""
        email = "not.registered@mergington.edu"
        
        response = client.delete(
            "/activities/Art Club/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()

    def test_root_redirect(self, client):
        """Test that root path redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        
        # Should redirect to /static/index.html
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
