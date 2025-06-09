import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from constants import STATS_COLUMNS

from step2_summarize import (
    read_csv_data,
    validate_years,
    clean_data,
    create_plot_directory,
    draw_plots
)

# Test data
@pytest.fixture
def valid_data():
    return pd.DataFrame({
        'year': [2020, 2021, 2022, 2020, 2021, 2022, 2020, 2021, 2022, 2022],
        'teamName': ['Arsenal', 'Arsenal', 'Arsenal', 'Chelsea', 'Chelsea', 'Chelsea', 'Liverpool', 'Liverpool', 'Liverpool', 'LiverpoolError'],
        'won': [15, 20, 25, 18, 22, 28, 16, 21, 26, 26],
        'draw': [5, 4, 3, 6, 5, 4, 7, 6, 5, 5],
        'lost': [8, 6, 4, 7, 5, 3, 8, 6, 4, 4],
        'goalsFor': [45, 55, 65, 48, 58, 68, 46, 56, 66, 66],
        'goalsAgainst': [35, 25, 15, 38, 28, 18, 36, 26, 16, 16]
    })

@pytest.fixture
def data_with_missing():
    df = pd.DataFrame({
        'year': [2020, 2021, 2022, 2020, 2021, 2022, 2020, 2021, 2022],
        'teamName': ['Arsenal', 'Arsenal', 'Arsenal', 'Chelsea', 'Chelsea', 'Chelsea', 'Liverpool', 'Liverpool', 'Liverpool'],
        'won': [15, np.nan, 25, 18, 22, 28, 16, 21, 26],
        'draw': [5, 4, 3, 6, 5, 4, 7, 6, 5],
        'lost': [8, 6, 4, 7, 5, 3, 8, 6, 4],
        'goalsFor': [45, 55, 65, 48, 58, 68, 46, 56, 66],
        'goalsAgainst': [35, 25, 15, 38, 28, 18, 36, 26, 16]
    })
    return df

# Test read_csv_data function
def test_read_csv_data_success(tmp_path):
    # Create temporary CSV file
    df = pd.DataFrame({
        'year': [2020],
        'teamName': ['Arsenal'],
        'won': [15],
        'draw': [5],
        'lost': [8],
        'goalsFor': [45],
        'goalsAgainst': [35]
    })
    file_path = tmp_path / "test.csv"
    df.to_csv(file_path, index=False)
    
    # Test reading
    result = read_csv_data(str(file_path))
    assert result is not None
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert result.iloc[0]['teamName'] == 'Arsenal'

def test_read_csv_data_file_not_found():
    result = read_csv_data('nonexistent.csv')
    assert result is None

# Test validate_years function
def test_validate_years_success(valid_data):
    is_valid, message = validate_years(valid_data)
    assert is_valid is True
    assert "Year verification passed" in message

def test_validate_years_invalid_format():
    df = pd.DataFrame({'year': ['2020', '2021']})
    is_valid, message = validate_years(df)
    assert is_valid is False
    assert "Year format wrong" in message

def test_validate_years_out_of_range():
    df = pd.DataFrame({'year': [1990, 2021]})
    is_valid, message = validate_years(df)
    assert is_valid is False
    assert "Year out of range" in message

# Test clean_data function
def test_clean_data_success(data_with_missing):
    result = clean_data(data_with_missing)
    assert result is not None
    assert not result['won'].isnull().any()
    assert result['won'].dtype in ['int64', 'float64']

def test_clean_data_invalid_years():
    df = pd.DataFrame({
        'year': [1990, 2021],
        'teamName': ['TeamA', 'TeamB'],
        'won': [15, 20],
        'draw': [5, 4],
        'lost': [8, 6],
        'goalsFor': [45, 55],
        'goalsAgainst': [35, 25]
    })
    result = clean_data(df)
    assert result is None


# Test create_plot_directory function
def test_create_plot_directory_success(tmp_path):
    plots_dir = tmp_path / "test_plots"
    result = create_plot_directory(str(plots_dir))
    assert result is True
    assert plots_dir.exists()

# Test draw_plots function
def test_draw_plots_success(valid_data, tmp_path):
    plots_dir = tmp_path / "premier_league_plots"
    with patch('matplotlib.pyplot.figure') as mock_figure, \
         patch('matplotlib.pyplot.savefig') as mock_savefig, \
         patch('matplotlib.pyplot.close') as mock_close, \
         patch('seaborn.barplot') as mock_barplot:
        mock_figure.return_value = MagicMock()
        mock_barplot.return_value = MagicMock()
        draw_plots(valid_data)
        assert mock_savefig.call_count == len(STATS_COLUMNS)  # Use length of STATS_COLUMNS
        assert mock_close.call_count == len(STATS_COLUMNS)

def test_draw_plots_no_data():
    with patch('matplotlib.pyplot.savefig') as mock_savefig:
        draw_plots(None)
        mock_savefig.assert_not_called()
