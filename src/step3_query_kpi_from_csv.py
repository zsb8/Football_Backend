import json
import os

def is_aws_environment():
    """
    Check if the code is running in AWS Lambda environment
    """
    return 'AWS_LAMBDA_FUNCTION_NAME' in os.environ

if is_aws_environment():
    from src.step2_summarize import read_csv_data
    from src.utils.constants import CSV_FILENAME
else:
    from step2_summarize import read_csv_data
    from utils.constants import CSV_FILENAME

def main(event=None):
    df = read_csv_data(CSV_FILENAME)
    if event:
        payload = json.loads(event['body']) 
        start_year = payload['StartYear']
        end_year = payload['EndYear']
        team_name_list = payload['TeamNameList']
        kpi_name = payload['KPIName']
    else:
        start_year = 2023
        end_year = 2024
        team_name_list = ['Manchester City FC', 'Arsenal FC']
        kpi_name = 'won'

    year_filter = (df['year'] >= start_year) & (df['year'] <= end_year)
    
    if team_name_list and len(team_name_list) > 0:
        team_filter = df['teamName'].isin(team_name_list)
        filtered_df = df[year_filter & team_filter]
    else:
        filtered_df = df[year_filter]
    
    filtered_df = filtered_df[['year', 'teamName', kpi_name]]
    
    print("Filtered data:")
    print(filtered_df)
    
    return {
        "Result": filtered_df.to_dict(orient='records')
    }

if __name__ == "__main__":
    main()