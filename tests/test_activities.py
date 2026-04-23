"""Test suite for FastAPI activities endpoints using AAA (Arrange-Act-Assert) pattern"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_list(self, client):
        """
        Test that GET /activities returns a list of activities.
        
        AAA Pattern:
        - Arrange: Client is ready to make requests
        - Act: Send GET request to /activities
        - Assert: Verify response status is 200 and response is a dict
        """
        # Arrange
        # (client fixture is already set up)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert len(response.json()) > 0
    
    def test_get_activities_has_expected_fields(self, client):
        """
        Test that each activity has the expected fields.
        
        AAA Pattern:
        - Arrange: Client is ready to make requests
        - Act: Send GET request to /activities and iterate through results
        - Assert: Verify each activity has required fields
        """
        # Arrange
        expected_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        assert isinstance(activities, dict)
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)
            assert expected_fields.issubset(activity_data.keys()), \
                f"Activity '{activity_name}' missing expected fields"
            assert isinstance(activity_data["participants"], list)
            assert activity_data["max_participants"] > 0


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_activity_success(self, client):
        """
        Test successfully signing up for an activity.
        
        AAA Pattern:
        - Arrange: Get initial activity state and prepare signup data
        - Act: Sign up a new student for an activity
        - Assert: Verify response status is 200 and participant count increased
        """
        # Arrange
        activity_name = "Basketball Team"
        student_email = "test_student@mergington.edu"
        
        # Get current participant count
        response_before = client.get("/activities")
        initial_count = len(response_before.json()[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        response_after = client.get("/activities")
        final_count = len(response_after.json()[activity_name]["participants"])
        assert final_count == initial_count + 1
        assert student_email in response_after.json()[activity_name]["participants"]
    
    def test_signup_activity_duplicate(self, client):
        """
        Test that signup fails when student is already registered.
        
        AAA Pattern:
        - Arrange: Sign up a student for an activity
        - Act: Attempt to sign up the same student again
        - Assert: Verify response status is 400 and error message indicates duplicate signup
        """
        # Arrange
        activity_name = "Drama Club"
        student_email = "duplicate_signup@mergington.edu"
        
        # First signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Act: Try to sign up again with same email
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "already signed up" in response.json()["detail"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """
        Test successfully unregistering from an activity.
        
        AAA Pattern:
        - Arrange: Sign up for an activity first
        - Act: Unregister from that activity
        - Assert: Verify response status is 200 and participant count decreased
        """
        # Arrange
        activity_name = "Art Club"
        student_email = "unregister_test@mergington.edu"
        
        # First, sign up for the activity
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Verify student was added
        response_before = client.get("/activities")
        initial_count = len(response_before.json()[activity_name]["participants"])
        assert student_email in response_before.json()[activity_name]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify participant was removed
        response_after = client.get("/activities")
        final_count = len(response_after.json()[activity_name]["participants"])
        assert final_count == initial_count - 1
        assert student_email not in response_after.json()[activity_name]["participants"]
    
    def test_unregister_not_registered(self, client):
        """
        Test that unregister fails when student is not signed up.
        
        AAA Pattern:
        - Arrange: Identify an activity and student not signed up for it
        - Act: Attempt to unregister from that activity
        - Assert: Verify response status is 400 and error message is appropriate
        """
        # Arrange
        activity_name = "Drama Club"
        student_email = "never_signed_up@mergington.edu"
        
        # Verify student is not in the activity
        response_before = client.get("/activities")
        assert student_email not in response_before.json()[activity_name]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "not signed up" in response.json()["detail"]
