import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path
from datetime import datetime
import boto3
import io


def is_aws_environment():
    """
    Check if the code is running in AWS Lambda environment
    """
    return 'AWS_LAMBDA_FUNCTION_NAME' in os.environ


if is_aws_environment():
    from src.utils.constants import STATS_COLUMNS, CSV_FILENAME, S3_FOLDER_PLOTS, S3_BUCKET_NAME
else:
    from utils.constants import STATS_COLUMNS, CSV_FILENAME, S3_FOLDER_PLOTS, S3_BUCKET_NAME


def save_plot_to_s3(plt, filename, bucket_name, key):
    """
    Save plot to S3 bucket
    """
    try:
        s3_client = boto3.client('s3')
        # Save plot to a temporary buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        
        # Upload to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=buffer
        )
        print(f"Plot saved to s3://{bucket_name}/{key}")
        return True
    except Exception as e:
        print(f"Error saving plot to S3: {str(e)}")
        return False

def read_csv_data(file_path):
    """
    Read data from a CSV file with error handling.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pandas.DataFrame: The loaded data or None if there was an error
    """
    try:
        s3_client = boto3.client('s3')
        bucket_name = 'zsbtest'
        object_key = 'football/data/premier_league_stats.csv'

        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read()

        df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
        if df.empty:
            print(f"Error: File '{file_path}' is empty.")
            return None
            
        print(f"Successfully loaded data from {file_path}")
        print("Data preview:")
        print(df.head())
        return df
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except pd.errors.EmptyDataError:
        print(f"Error: File '{file_path}' is empty.")
        return None
    except pd.errors.ParserError as e:
        print(f"Error parsing CSV file: {str(e)}")
        return None
    except Exception as e:
        print(f"Error reading file '{file_path}': {str(e)}")
        return None

def validate_years(df):
    """
    Validate years in the dataset.
    Checks for:
    1. Year format (should be 4-digit number)
    2. Year range (should be within Premier League history)
    3. Year consistency (should be consecutive if required)
    
    Args:
        df (pandas.DataFrame): Input DataFrame containing team data
        
    Returns:
        tuple: (bool, str) - (is_valid, message)
    """
    if df is None:
        return False, "No data to validate"
        
    try:
        # Check year format
        if not df['year'].dtype in ['int64', 'int32']:
            return False, "Year format wrong: It should be int."
            
        # Get all years
        years = sorted(df['year'].unique())
        
        # Check year range (Premier League starts in 1992)
        if min(years) < 1992:
            return False, f"! Year out of range: year {min(years)} earlier than the start of the Premier League 1992"
        if max(years) > datetime.now().year:
            return False, f"! Year out of range: newest year {max(years)} late than now {datetime.now().year}"
            
        # Check if the year is consecutive (optional, depends on business needs)
        if len(years) > 1:
            expected_years = list(range(min(years), max(years) + 1))
            if years != expected_years:
                return False, f"Years are not consecutive: Years found {years}，Expected consecutive years {expected_years}"
        
        return True, f"Year verification passed：{years}"
        
    except Exception as e:
        return False, f"Year validation error：{str(e)}"

def clean_data(df):
    """
    Clean the data by handling missing values using median imputation.
    Only processes columns that actually have missing values.
    
    Args:
        df (pandas.DataFrame): Input DataFrame containing team data
        
    Returns:
        pandas.DataFrame: Cleaned DataFrame with missing values filled or None if there was an error
    """
    if df is None:
        return None
        
    try:
        # First verify the year
        is_valid, message = validate_years(df)
        if not is_valid:
            print(f"\nYear validation failed:{message}")
            return None
        print(f"\n{message}")
        
        # Use STATS COLUMNS as the numeric column to be checked
        numeric_columns = STATS_COLUMNS
        
        # Check for missing values
        missing_values = df[numeric_columns].isnull().sum()
        if missing_values.any():
            for column, count in missing_values[missing_values > 0].items():
                print(f"{column}: {count} missing values")
            df_cleaned = df.copy()
            for column in missing_values[missing_values > 0].index:
                median_value = df[column].median()
                df_cleaned[column] = df[column].fillna(median_value)
                print(f"Use the median {median_value:.2f} fill {column}")
            print("\nData cleaning completed")
            return df_cleaned
        else:
            print("\nThere are no missing values ​in the data")
            return df
            
    except Exception as e:
        print(f"Error in data cleaning: {str(e)}")
        return None

def align_team_name(df):
    """
    Align team names across different years to ensure consistent comparison.
    Returns a DataFrame containing only teams that exist in all years.
    
    Args:
        df (pandas.DataFrame): Input DataFrame containing team data
        
    Returns:
        pandas.DataFrame: Filtered DataFrame with aligned team names or None if there was an error
    """
    if df is None:
        return None
        
    try:
        all_years = df['year'].unique()
        print(f"All year: {all_years}")
        teams_by_year = df.groupby('year')['teamName'].unique()

        # Find teams that exist in all years
        common_teams = set(teams_by_year.iloc[0])
        for year_teams in teams_by_year[1:]:
            common_teams = common_teams.intersection(set(year_teams))

        if not common_teams:
            print("Warning: No common teams found across all years")
            return None

        print("\nThe teams that exist in all years:")
        print(sorted(list(common_teams)))

        # Only keep data for teams that exist in all years
        df_filtered = df[df['teamName'].isin(common_teams)]

        # Show data by season and team group
        print("\nData grouped by season and team (only teams that existed in all years are included):")
        agg_dict = {col: 'sum' for col in STATS_COLUMNS}
        print(df_filtered.groupby(['year', 'teamName']).agg(agg_dict).reset_index())
        
        return df_filtered
    except KeyError as e:
        print(f"Error: Missing required column {e}")
        return None
    except Exception as e:
        print(f"Error in team name alignment: {str(e)}")
        return None

def create_plot_directory(plots_dir):
    """
    Create directory for plots with error handling
    """
    try:
        Path(plots_dir).mkdir(parents=True, exist_ok=True)
        return True
    except PermissionError:
        print(f"Error: Permission denied when creating directory {plots_dir}")
        return False
    except Exception as e:
        print(f"Error creating directory {plots_dir}: {str(e)}")
        return False

def sort_dataframe(df, stat):
    """
    Sort the DataFrame by the specified statistic in descending order.
    
    Args:
        df (pandas.DataFrame): Input DataFrame containing team data
        stat (str): The statistic column to sort by
        
    Returns:
        pandas.DataFrame: Sorted DataFrame
    """
    try:
        df_sorted = df.groupby(['teamName', 'year'])[stat].sum().reset_index()
        team_means = df_sorted.groupby('teamName')[stat].mean()
        sorted_teams = team_means.sort_values(ascending=False).index
        df_sorted = df[df['teamName'].isin(sorted_teams)].copy()
        df_sorted['teamName'] = pd.Categorical(df_sorted['teamName'], categories=sorted_teams, ordered=True)
        return df_sorted.sort_values(['teamName', 'year'])
    except Exception as e:
        print(f"Error sorting data for {stat}: {str(e)}")
        return df

def draw_plots(df_filtered):
    """
    Create and save plots for each statistic in the data.
    """
    if df_filtered is None:
        print("Error: No data available for plotting")
        return
        
    # Create a directory for plots if it doesn't exist (only for local environment)
    plots_dir = 'premier_league_plots'
    if not is_aws_environment() and not create_plot_directory(plots_dir):
        return

    for stat in STATS_COLUMNS:
        try:
            df_sorted = sort_dataframe(df_filtered, stat)
            plt.figure(figsize=(14, 5))
            sns.barplot(
                data=df_sorted,
                x='teamName',
                y=stat,
                hue='year'
            )
            plt.title(f'{stat} by Team and Year')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Save the plot based on environment
            filename = f'{stat}_by_team_and_year.png'
            if is_aws_environment():
                # Save to S3 when running in AWS
                s3_key = f"{S3_FOLDER_PLOTS}{filename}"
                save_plot_to_s3(plt, filename, S3_BUCKET_NAME, s3_key)
            else:
                # Save locally when running on local machine
                local_path = f'{plots_dir}/{filename}'
                plt.savefig(local_path, dpi=300, bbox_inches='tight')
                print(f"Saved plot to {local_path}")
            
            plt.close()  # Close the figure to free memory
        except Exception as e:
            print(f"Error creating plot for {stat}: {str(e)}")
            plt.close()  # Ensure figure is closed even if there's an error
            continue

def main():
    try:
        # Read the data
        df = read_csv_data(CSV_FILENAME)
        if df is not None:
            # Clean the data
            df_cleaned = clean_data(df)
            if df_cleaned is not None:
                # Align team names across years
                # df_filtered = align_team_name(df_cleaned)
                df_filtered = df_cleaned
                # Create and save the plots
                draw_plots(df_filtered)
        else:
            print("Program terminated due to data loading error.")
    except Exception as e:
        print(f"Unexpected error in main: {str(e)}")

if __name__ == "__main__":
    main()



