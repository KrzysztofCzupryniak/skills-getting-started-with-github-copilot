"""Pytest configuration and fixtures for FastAPI tests"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient instance for testing FastAPI endpoints.
    
    The TestClient allows us to make requests to the FastAPI app without 
    running a live server.
    """
    return TestClient(app)
