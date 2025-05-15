import pytest
import sys
sys.path.append('/app')  
from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    return app.test_client()

def test_get_message(client):
    """Test the /api/message endpoint."""
    response = client.get('/api/message')
    assert response.status_code == 200
    assert response.json == {"message": "Hello from the backend!"}