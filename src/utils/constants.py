import os

# Columns for Premier League statistics aggregation
STATS_COLUMNS = ['won', 'draw', 'lost', 'goalsFor', 'goalsAgainst']

S3_BUCKET_NAME = 'zsbtest'
S3_FOLDER_DATA = 'football/data/'
S3_FOLDER_PLOTS = 'football/premier_league_plots/'
# File names
CSV_FILENAME = 'data/premier_league_stats.csv'

# API related constants
API_TOKEN = '12abfbaacdab48bc8948ed6061925e1f'
# API_TOKEN = os.getenv('FOOTBALL_API_TOKEN')
API_BASE_URL = 'https://api.football-data.org/v4/competitions/PL' 


