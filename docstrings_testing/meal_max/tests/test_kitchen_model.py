import pytest
import sqlite3
from meal_max.models import kitchen_model
from meal_max.models.kitchen_model import Meal

@pytest.fixture
def sample_meal():
    return Meal(1, "Spaghetti", "Italian", 12.5, "MED")

@pytest.fixture
def mock_db_connection(mocker):
    """Mock the get_db_connection function to avoid real database calls."""
    return mocker.patch("meal_max.utils.sql_utils.get_db_connection")

#def create_meal
#def clear_meals
#def delete_meal
#def get_leaderboard
#def get_meal_by_id
#def get_meal_by_name
#def update_meal_stats
