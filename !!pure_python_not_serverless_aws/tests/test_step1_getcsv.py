import pytest
from unittest.mock import patch
import pandas as pd
from step1_getcsv import get_league_standings, save_to_csv
from constants import CSV_FILENAME

# Fixture for mock API response data
@pytest.fixture
def mock_response_data():
    return {
        'filters': {'season': 2023},
        'season': {
            'startDate': '2023-08-11',
            'endDate': '2024-05-19'
        },
        'standings': [{
            'type': 'TOTAL',
            'table': [{
                'team': {'name': 'Arsenal'},
                'won': 20,
                'draw': 5,
                'lost': 3,
                'goalsFor': 60,
                'goalsAgainst': 25
            }]
        }]
    }

def test_get_league_standings_success(mock_response_data):
    with patch('requests.get') as mock_get:
        # Mock successful API response
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data

        result = get_league_standings(2023)
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['teamName'] == 'Arsenal'
        assert result[0]['won'] == 20

def test_get_league_standings_api_error():
    with patch('requests.get') as mock_get:
        # Mock API error
        mock_get.side_effect = Exception("API Error")
        
        with pytest.raises(Exception) as exc_info:
            get_league_standings(2023)
        assert str(exc_info.value) == "API Error"

def test_get_league_standings_invalid_response():
    with patch('requests.get') as mock_get:
        # Mock invalid response
        mock_response = mock_get.return_value
        mock_response.status_code = 404
        
        result = get_league_standings(2023)
        assert result == []

def test_save_to_csv_success():
    # Create test DataFrame with all required columns
    test_data = {
        'year': [2023],
        'teamName': ['Arsenal']
    }
    df = pd.DataFrame(test_data)
    # Mock file operations
    with patch('pandas.DataFrame.to_csv') as mock_to_csv:
        result = save_to_csv(df, CSV_FILENAME)
        assert result is True
        mock_to_csv.assert_called_once()

def test_save_to_csv_permission_error():
    # Create test DataFrame with all required columns
    test_data = {
        'year': [2023],
        'teamName': ['Arsenal']
    }
    df = pd.DataFrame(test_data)
    with patch('pandas.DataFrame.to_csv', side_effect=PermissionError):
        result = save_to_csv(df, CSV_FILENAME)
        assert result is False

def test_save_to_csv_general_error():
    # Create test DataFrame with all required columns
    test_data = {
        'year': [2023],
        'teamName': ['Arsenal']
    }
    df = pd.DataFrame(test_data)
    # Mock general error
    with patch('pandas.DataFrame.to_csv', side_effect=Exception("General error")):
        result = save_to_csv(df, CSV_FILENAME)
        assert result is False
