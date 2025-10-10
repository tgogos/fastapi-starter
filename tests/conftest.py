# Test configuration
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routes.items import items_storage

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture(autouse=True)
def clear_items_storage():
    """Clear items storage before each test to ensure test isolation."""
    items_storage.clear()
    yield
    items_storage.clear()

@pytest.fixture
def sample_item_data():
    """Sample item data for testing."""
    return {
        "name": "Test Item",
        "description": "A test item for testing purposes"
    }

@pytest.fixture
def sample_item_update_data():
    """Sample item update data for testing."""
    return {
        "name": "Updated Test Item",
        "description": "An updated test item"
    }
