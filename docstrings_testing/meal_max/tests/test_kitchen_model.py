import pytest
import sqlite3
from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    delete_meal,
    get_meal_by_id,
    update_meal_stats
)
from meal_max.utils.sql_utils import get_db_connection

# Fixtures#

@pytest.fixture
def mock_db_cursor(mocker):
    """Mock database connection and cursor to avoid actual DB interaction."""
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor

    # Patch get_db_connection to return the mocked connection#
    mocker.patch("meal_max.utils.sql_utils.get_db_connection", return_value=mock_conn)
    return mock_cursor


@pytest.fixture
def sample_meal():
    """Sample Meal object for consistency in tests."""
    return Meal(1, "Sample Meal", "Cuisine Type", 15.00, "MED")



# Test Cases for Adding Meals#


def test_create_meal_success(mock_db_cursor):
    """Ensure create_meal adds a meal to the database correctly."""
    create_meal(meal="Meal 1", cuisine="Cuisine 1", price=10.0, difficulty="LOW")
    mock_db_cursor.execute.assert_called_once_with(
        "INSERT INTO meals (meal, cuisine, price, difficulty) VALUES (?, ?, ?, ?)",
        ("Meal 1", "Cuisine 1", 10.0, "LOW")
    )


def test_create_duplicate_meal(mock_db_cursor):
    """Check that adding a duplicate meal raises a ValueError."""
    mock_db_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed")
    with pytest.raises(ValueError, match="Meal with name 'Meal 1' already exists"):
        create_meal(meal="Meal 1", cuisine="Cuisine 1", price=10.0, difficulty="LOW")


# Test Cases for Deleting Meals#


def test_delete_meal_success(mock_db_cursor):
    """Ensure delete_meal updates the meal status to deleted."""
    mock_db_cursor.fetchone.return_value = (False,)  # Meal is not already deleted#
    delete_meal(1)
    mock_db_cursor.execute.assert_any_call("UPDATE meals SET deleted = TRUE WHERE id = ?", (1,))


def test_delete_meal_already_deleted(mock_db_cursor):
    """Check that deleting an already deleted meal raises ValueError."""
    mock_db_cursor.fetchone.return_value = (True,)  # Meal is already marked deleted#
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        delete_meal(1)


def test_delete_meal_not_found(mock_db_cursor):
    """Verify that deleting a non-existent meal raises ValueError."""
    mock_db_cursor.fetchone.return_value = None  # Meal not found#
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        delete_meal(1)



# Test Cases for Retrieving Meals by ID#

def test_get_meal_by_id_success(mock_db_cursor, sample_meal):
    """Ensure get_meal_by_id retrieves a meal if it exists in the DB."""
    mock_db_cursor.fetchone.return_value = (1, "Sample Meal", "Cuisine Type", 15.00, "MED", False)
    meal = get_meal_by_id(1)

    # Compare individual attributes for clarity#
    assert meal.id == sample_meal.id
    assert meal.meal == sample_meal.meal
    assert meal.cuisine == sample_meal.cuisine
    assert meal.price == sample_meal.price
    assert meal.difficulty == sample_meal.difficulty


def test_get_meal_by_id_not_found(mock_db_cursor):
    """Check that retrieving a meal by invalid ID raises ValueError."""
    mock_db_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        get_meal_by_id(1)


# Test Cases for Updating Meal Stats#

def test_update_meal_stats_win(mock_db_cursor):


"""Ensure update_meal_stats increments win stats when a meal wins."""
    mock_db_cursor.fetchone.return_value = (False,)  # Meal not deleted#
    update_meal_stats(1, "win")
    mock_db_cursor.execute.assert_any_call(
        "UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?", (1,)
    )


def test_update_meal_stats_loss(mock_db_cursor):
    """Ensure update_meal_stats increments battle count when a meal loses."""
    mock_db_cursor.fetchone.return_value = (False,)  # Meal not deleted#
    update_meal_stats(1, "loss")
    mock_db_cursor.execute.assert_any_call(
        "UPDATE meals SET battles = battles + 1 WHERE id = ?", (1,)
    )


def test_update_meal_stats_invalid_result(mock_db_cursor):
    """Check that invalid result in update_meal_stats raises ValueError."""
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'"):
        update_meal_stats(1, "draw")
