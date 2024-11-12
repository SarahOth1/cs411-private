import pytest
from contextlib import contextmanager
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()


"""Fixtures providing sample meals for the tests."""
@pytest.fixture
def sample_meal1():
    return Meal(1, 'Tikka Masala', 'Indian', 25.0, 'MED')

@pytest.fixture
def sample_meal2():
    return Meal(2, 'Pasta', 'Italian', 20.0, 'LOW')

@pytest.fixture
def sample_meal3():
    return Meal(3, 'Anything', 'Saudi', 23.0, 'HIGH')


@pytest.fixture
def sample_battle(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]

@pytest.fixture
def mock_db(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None
    
    # Mock the get_db_connection function context manager
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_conn, mock_cursor

@pytest.fixture
def mock_update_meal_stats(mocker):
    """Mock the update_meal_stats function for testing purposes."""
    return mocker.patch("models.battle_model.update_meal_stats")


@pytest.fixture
def mock_requests_get(mocker):
    mock_response = mocker.Mock()
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response

#####################
    # Test Battle Management Functions
#####################
def test_battle_error(battle_model, sample_meal1, caplog):
    """Test the VlaueError of battle between if combatants are < 2."""
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()
    

def test_battle(mock_requests_get, battle_model, sample_meal1, sample_meal2):
    """Test the winner of battle between first 2 combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    mock_requests_get.text = "0.02"
    winnerMeal = battle_model.battle()
    assert winnerMeal == sample_meal1.meal

def test_battle2(mock_requests_get, battle_model, sample_meal1, sample_meal2):
    """Test the winner of battle between first 2 combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    mock_requests_get.text = "0.4"
    winnerMeal = battle_model.battle()
    assert winnerMeal == sample_meal2.meal
    

def test_clear_combatants(battle_model, sample_meal1):
    """Test clearing the entire combatants list."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Playlist should be empty after clearing"

def test_get_combatants(battle_model, sample_meal1, sample_meal2):
    """Test successfully retrieving all combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    all_coms = battle_model.get_combatants()
    assert len(all_coms) == 2
    assert all_coms[0].id == 1
    assert all_coms[1].id == 2

def test_prep_combatant(battle_model, sample_meal1):
    """Test adding a combatant to the combatants list."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'Tikka Masala'

def test_prep_combatant_error(battle_model, sample_meal1, sample_meal2, sample_meal3):
    """Test failing to add a combatant to the full combatants list."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal3)

def test_get_battle_score(battle_model, sample_meal1):
    """Test getting the battle score."""
    difficulty_modifier = {"HIGH": 1, "MED": 2, "LOW": 3}
    score = battle_model.get_battle_score(sample_meal1)
    assert score == (sample_meal1.price * len(sample_meal1.cuisine)) - difficulty_modifier[sample_meal1.difficulty]
