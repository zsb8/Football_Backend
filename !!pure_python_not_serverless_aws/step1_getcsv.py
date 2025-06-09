import requests
import json
import pandas as pd
from datetime import datetime
import os
from constants import STATS_COLUMNS, CSV_FILENAME, API_TOKEN, API_BASE_URL

def get_league_standings(season):
    uri = f'{API_BASE_URL}/standings?season={season}'
    headers = { 'X-Auth-Token': API_TOKEN }
    try:
        response = requests.get(uri, headers=headers)
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None
    if response.status_code == 200:
        try:
            data = response.json()
            total_standings = None
         
            for standing in data['standings']:
                if standing['type'] == 'TOTAL':
                    total_standings = standing
                    break
            if total_standings is None:
                print(f"Can't find TOTAL standings data")
                return []   
            else:
                teams_data = []
                for team in total_standings['table']:
                    try:
                        team_data = {
                            'year': data['filters']['season'],
                            'startDate': data['season']['startDate'],
                            'endDate': data['season']['endDate'],
                            'teamName': team['team']['name']
                        }
                        # Use STATS_COLUMNS
                        for stat in STATS_COLUMNS:
                            team_data[stat] = team[stat]
                        teams_data.append(team_data)
                    except KeyError as e:
                        print(f"Error processing team data: Missing key {e}")
                        continue
                return teams_data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return None
        except KeyError as e:
            print(f"Error accessing data: Missing key {e}")
            return None
    else:
        print(f"Get {season} season data failed: {response.status_code}")
        return []

def save_to_csv(df, filename):
    """
    Save DataFrame to CSV file with error handling
    """
    try:
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\nData save as {filename}")
        return True
    except PermissionError:
        print(f"Error: Permission denied when saving to {filename}")
        return False
    except Exception as e:
        print(f"Error saving to CSV: {str(e)}")
        return False

def judge_incremental(df, filename):
    """
    Compare new data with existing CSV file and determine if incremental update is needed
    Returns True if save is needed, False if no update needed
    """
    try:
        if not os.path.exists(filename):
            print(f"File {filename} does not exist. Will create new file.")
            return True
            
        existing_csv_df = pd.read_csv(filename)
        
        # Create composite key for comparison
        df['composite_key'] = df['year'].astype(str) + '_' + df['teamName']
        existing_csv_df['composite_key'] = existing_csv_df['year'].astype(str) + '_' + existing_csv_df['teamName']
        
        # Find new records
        new_records = df[~df['composite_key'].isin(existing_csv_df['composite_key'])]
        
        if len(new_records) > 0:
            print(f"Found {len(new_records)} new records to add")
            return True
        else:
            print("No new records found. Skipping save operation.")
            return False
            
    except Exception as e:
        print(f"Error in judge_incremental: {str(e)}")
        return True  # If there's an error, we'll save to be safe

def main():
    try:
        years = [2020, 2021, 2022, 2023, 2024]
        all_data = []
        for year in years:
            season_data = get_league_standings(year)
            if season_data is not None:
                all_data.extend(season_data)
            else:
                print(f"Warning: Failed to get data for year {year}")

        if not all_data:
            print("Error: No data was collected from any year")
            return

        try:
            df = pd.DataFrame(all_data)
        except Exception as e:
            print(f"Error creating DataFrame: {str(e)}")
            return

        print(df.head())
        print(df.describe())

        try:
            print("\nData by season and team:")
            agg_dict = {col: 'sum' for col in STATS_COLUMNS}
            print(df.groupby(['year', 'teamName']).agg(agg_dict).reset_index())
        except Exception as e:
            print(f"Error calculating statistics: {str(e)}")

        # Determine whether incremental update and save are required
        if judge_incremental(df, CSV_FILENAME):
            save_to_csv(df, CSV_FILENAME)

    except Exception as e:
        print(f"Unexpected error in main: {str(e)}")

if __name__ == "__main__":
    main()


