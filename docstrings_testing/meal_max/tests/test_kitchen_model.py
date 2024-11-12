import pytest
from meal_max.models.kitchen_model import Meal, create_meal, delete_meal, get_meal_by_id, update_meal_stats
from meal_max.utils.sql_utils import get_db_connection
import sqlite3
import os
import logging

# Fixtures

@pytest.fixture
def mock_db_cursor(mocker):
    """Mocks the database connection and cursor."""
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor

    # Patch get_db_connection to return the mock connection
    mocker.patch("meal_max.utils.sql_utils.get_db_connection", return_value=mock_conn)
    return mock_cursor


@pytest.fixture
def sample_meal():
    """Returns a sample meal with predefined attributes."""
    return Meal(5, "Steak Frites", "French", 25.50, "HIGH")


# Test Cases for Creating and Deleting Meals

def test_create_meal_success(mock_db_cursor):
    """Tests creating a new meal in the database."""
    create_meal(meal="Steak Frites", cuisine="French", price=25.50, difficulty="HIGH")
    mock_db_cursor.execute.assert_called_once_with(
        "INSERT INTO meals (meal, cuisine, price, difficulty) VALUES (?, ?, ?, ?)",
        ("Steak Frites", "French", 25.50, "HIGH")
    )


def test_create_duplicate_meal(mock_db_cursor):
    """Checks if creating a duplicate meal raises an error."""
    mock_db_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed")
    with pytest.raises(ValueError, match="Meal with this name already exists"):
        create_meal(meal="Steak Frites", cuisine="French", price=25.50, difficulty="HIGH")


def test_delete_meal_success(mock_db_cursor):
    """Tests marking a meal as deleted."""
    mock_db_cursor.fetchone.return_value = (False,)  # Meal is not deleted
    delete_meal(5)
    mock_db_cursor.execute.assert_any_call("UPDATE meals SET deleted = TRUE WHERE id = ?", (5,))


def test_delete_meal_already_deleted(mock_db_cursor):
    """Checks if deleting an already deleted meal raises an error."""
    mock_db_cursor.fetchone.return_value = (True,)  # Meal is already marked deleted
    with pytest.raises(ValueError, match="Meal with ID 5 is already deleted"):
        delete_meal(5)


def test_delete_meal_not_found(mock_db_cursor):
    """Tests deleting a meal that doesn’t exist."""
    mock_db_cursor.fetchone.return_value = None  # Meal not found
    with pytest.raises(ValueError, match="Meal with ID 5 not found"):
        delete_meal(5)


# Test Cases for Retrieving Meals by ID

def test_get_meal_by_id_success(mock_db_cursor, sample_meal):
    """Tests retrieving a meal by ID when it exists."""
    mock_db_cursor.fetchone.return_value = (5, "Steak Frites", "French", 25.50, "HIGH", False)
    meal = get_meal_by_id(5)
    assert meal == sample_meal, f"Expected {sample_meal}, got {meal}"


def test_get_meal_by_id_not_found(mock_db_cursor):
    """Checks if retrieving a non-existent meal by ID raises an error."""
    mock_db_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 5 not found"):
        get_meal_by_id(5)


# Test Cases for Updating Meal Stats

def test_update_meal_stats_success(mock_db_cursor):
    """Tests updating meal stats with a win."""
    update_meal_stats(5, "win")
    mock_db_cursor.execute.assert_called_once_with(
        "UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?", (5,)
    )


def test_update_meal_stats_invalid_operation(mock_db_cursor):
    """Checks if an invalid result type raises an error."""
    with pytest.raises(ValueError, match="Invalid operation: draw"):
        update_meal_stats(5, "draw")
