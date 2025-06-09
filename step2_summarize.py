import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path
from datetime import datetime
from constants import STATS_COLUMNS, CSV_FILENAME

def read_csv_data(file_path):
    """
    Read data from a CSV file with error handling.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pandas.DataFrame: The loaded data or None if there was an error
    """
    try:
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' does not exist.")
            return None
            
        df = pd.read_csv(file_path)
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
        
    # Create a directory for plots if it doesn't exist
    plots_dir = 'premier_league_plots'
    if not create_plot_directory(plots_dir):
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
            
            # Save the plot
            filename = f'{plots_dir}/{stat}_by_team_and_year.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()  # Close the figure to free memory
            print(f"Saved plot to {filename}")
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
                # Create and save the plots
                draw_plots(df_cleaned)
        else:
            print("Program terminated due to data loading error.")
    except Exception as e:
        print(f"Unexpected error in main: {str(e)}")

if __name__ == "__main__":
    main()



