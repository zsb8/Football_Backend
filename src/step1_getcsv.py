import requests
import json
import pandas as pd
from datetime import datetime
import os
import boto3

def is_aws_environment():
    """
    Check if the code is running in AWS Lambda environment
    """
    return 'AWS_LAMBDA_FUNCTION_NAME' in os.environ


if is_aws_environment():
    from src.utils.constants import STATS_COLUMNS, CSV_FILENAME, API_TOKEN, API_BASE_URL,S3_BUCKET_NAME,S3_FOLDER_DATA
else:
    from utils.constants import STATS_COLUMNS, CSV_FILENAME, API_TOKEN, API_BASE_URL,S3_BUCKET_NAME,S3_FOLDER_DATA

def save_to_s3(df, bucket_name, key):
    """
    Save DataFrame to S3 bucket
    """
    try:
        s3_client = boto3.client('s3')
        csv_buffer = df.to_csv(index=False, encoding='utf-8-sig')
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=csv_buffer
        )
        print(f"\nData saved to s3://{bucket_name}/{key}")
        return True
    except Exception as e:
        print(f"Error saving to S3: {str(e)}")
        return False

def save_to_csv(df, filename):
    """
    Save DataFrame to CSV file with error handling
    """
    try:
        if is_aws_environment():
            # Save to S3 when running in AWS
            return save_to_s3(df, S3_BUCKET_NAME , S3_FOLDER_DATA + os.path.basename(filename))
        else:
            # Save locally when running on local machine
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\nData saved as {filename}")
            return True
    except PermissionError:
        print(f"Error: Permission denied when saving to {filename}")
        return False
    except Exception as e:
        print(f"Error saving to CSV: {str(e)}")
        return False

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

def judge_incremental(df, filename):
    """
    Compare new data with existing CSV file and determine if incremental update is needed
    Returns True if save is needed, False if no update needed
    """
    try:
        # Create composite key for comparison
        df['composite_key'] = df['year'].astype(str) + '_' + df['teamName']
        
        if is_aws_environment():
            # Check if file exists in S3
            s3_client = boto3.client('s3')
            try:
                response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=S3_FOLDER + os.path.basename(filename))
                existing_csv_df = pd.read_csv(response['Body'])
            except s3_client.exceptions.ClientError as e:
                if e.response['Error']['Code'] == '404':
                    print(f"File not found in S3. Will create new file.")
                    return True
                raise
        else:
            if not os.path.exists(filename):
                print(f"File {filename} does not exist. Will create new file.")
                return True
            existing_csv_df = pd.read_csv(filename)
        
        # Compare records
        existing_csv_df['composite_key'] = existing_csv_df['year'].astype(str) + '_' + existing_csv_df['teamName']
        new_records = df[~df['composite_key'].isin(existing_csv_df['composite_key'])]
        
        if len(new_records) > 0:
            print(f"Found {len(new_records)} new records to add")
            return True
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


