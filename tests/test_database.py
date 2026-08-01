import pytest
import sqlite3
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import Config
from database.db_connection import get_connection, initialize_database
from database.queries import insert_location, get_location_by_name

# Use an in-memory database for testing
@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    monkeypatch.setattr(Config, "DB_PATH", Path(":memory:"))
    
    # We need a custom get_connection for in-memory to persist across calls
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    def mock_get_connection():
        return conn
        
    monkeypatch.setattr("database.db_connection.get_connection", mock_get_connection)
    monkeypatch.setattr("database.queries.get_connection", mock_get_connection)
    
    # Initialize schema
    schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
    conn.executescript(schema_path.read_text())
    
    yield conn
    conn.close()

def test_insert_and_get_location():
    loc_id = insert_location("Test_Node", 13.0, 80.0, "Test Road")
    assert loc_id is not None
    
    loc = get_location_by_name("Test_Node")
    assert loc is not None
    assert loc["latitude"] == 13.0
    assert loc["city"] == "Chennai"
