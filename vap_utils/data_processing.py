"""
-----------------------------------------------------
Module: data_processing.py
Description: Functions for data preprocessing and time window expansion.
Author: Julen Berrueta Llona
Created: 2024-10-27
-----------------------------------------------------
"""

import pandas as pd
import numpy as np

def generate_backward_hourly_windows(df, hour_interval, outcome_date_col):
    """
    Generates backward hourly time windows from the specified outcome date,
    moving backward in fixed intervals while respecting the admission time as the lower boundary.

    Args:
    - df (pd.DataFrame): DataFrame with columns 'PatientID', 'AdmTime', 'DisTime', and the outcome date column.
    - hour_interval (int): The interval of hours to define each time window.
    - outcome_date_col (str): Column name indicating the outcome date.

    Returns:
    - pd.DataFrame: Expanded DataFrame with hourly intervals going backwards from the outcome date.
      The resulting DataFrame includes the following columns:
        - 'PatientID': Unique identifier for each patient.
        - 'hr': The negative offset in hours from the outcome date.
        - 'AdmTimeHourlyBegin': Start time of the hourly interval.
        - 'AdmTimeHourlyFinal': End time of the hourly interval.

    Example:
    --------
    >>> hour_interval = 24
    >>> expanded_df = generate_backward_hourly_windows(df, hour_interval, 'date_0')
    >>> expanded_df.head()

    This will generate 24-hour backward intervals from the 'date_0' column,
    creating time windows for each patient until their admission time.
    """

    # Calculate the maximum number of hourly intervals from outcome_date_col to AdmTime
    max_intervals = ((df[outcome_date_col] - df['AdmTime']) / pd.Timedelta(hours=hour_interval)).astype(int) + 1

    if max_intervals.empty:
        print(max_intervals)

    # Repeat patient IDs according to the number of backward intervals
    repeated_ids = df['PatientID'].repeat(max_intervals)

    # Create ranges of negative hours going backwards from outcome_date_col
    hours_range = np.concatenate([-(np.arange(intervals) + 1) * hour_interval for intervals in max_intervals])

    # Repeat AdmTime, DisTime, and outcome_date_col for each interval
    repeated_adm_time = df['AdmTime'].repeat(max_intervals)
    repeated_dis_time = df['DisTime'].repeat(max_intervals)
    repeated_outcome_date = df[outcome_date_col].repeat(max_intervals)

    # Create the expanded DataFrame
    hourly_data = pd.DataFrame({
        'PatientID': repeated_ids,
        'hr': hours_range,
        'AdmTime': repeated_adm_time,
        'DisTime': repeated_dis_time,
        outcome_date_col: repeated_outcome_date
    })

    # Calculate the starting time for each hourly interval going backwards
    hourly_data['AdmTimeHourlyBegin'] = hourly_data[outcome_date_col] + pd.to_timedelta(hourly_data['hr'], unit='h')

    # Calculate AdmTimeHourlyFinal by adding the hourly interval
    hourly_data['AdmTimeHourlyFinal'] = hourly_data['AdmTimeHourlyBegin'] + pd.to_timedelta(hour_interval, unit='h')

    # Adjust the limits to not go past AdmTime backwards
    hourly_data['AdmTimeHourlyBegin'] = np.where(hourly_data['AdmTimeHourlyBegin'] < hourly_data['AdmTime'],
                                                 hourly_data['AdmTime'], 
                                                 hourly_data['AdmTimeHourlyBegin'])
    
    # Adjust the limits to not go beyond DisTime forwards
    hourly_data['AdmTimeHourlyFinal'] = np.where(hourly_data['AdmTimeHourlyFinal'] > hourly_data['DisTime'],
                                                 hourly_data['DisTime'],
                                                 hourly_data['AdmTimeHourlyFinal'])

    # Drop unnecessary columns if desired
    hourly_data.drop(columns=['AdmTime', 'DisTime', outcome_date_col], inplace=True)

    return hourly_data.sort_values(["PatientID", "hr"], ascending=True)


def expand_hourly_from_admission_to_outcome(patients_hr, outcome_date_col):
    """
    Expands the DataFrame into 24-hour windows moving forward from AdmTime to the specified outcome date,
    advancing in 1-hour intervals.

    This function is designed to create rolling windows for inference or analysis from admission until an outcome.

    Args:
    - patients_hr (pd.DataFrame): DataFrame with columns 'PatientID', 'AdmTime', 'DisTime'.
    - outcome_date_col (str): Name of the column containing the final reference date (e.g., DisTime).

    Returns:
    - pd.DataFrame: Expanded DataFrame with 24-hour forward rolling windows.

    Example:
    --------
    >>> expanded_df = expand_hourly_from_admission_to_outcome(df, 'DisTime')
    >>> expanded_df.head()
    """

    # Replace missing values in the outcome_date_col with the current timestamp
    patients_hr[outcome_date_col] = patients_hr[outcome_date_col].fillna(pd.Timestamp.now())

    # Calculate the maximum number of 1-hour windows from AdmTime to the outcome date
    max_windows = ((patients_hr[outcome_date_col] - patients_hr['AdmTime']) / pd.Timedelta(hours=1)).astype(int) + 1

    # Repeat Patient IDs based on the number of forward windows
    repeated_ids = patients_hr['PatientID'].repeat(max_windows)

    # Create hour ranges starting from 0 moving forward
    hours_range = np.concatenate([np.arange(windows) for windows in max_windows])

    # Repeat AdmTime and outcome_date for each window
    repeated_adm_time = patients_hr['AdmTime'].repeat(max_windows)
    repeated_outcome_date = patients_hr[outcome_date_col].repeat(max_windows)

    # Create the expanded DataFrame
    rolling_data = pd.DataFrame({
        'PatientID': repeated_ids,
        'hr': hours_range,
        'AdmTime': repeated_adm_time,
        outcome_date_col: repeated_outcome_date
    })

    # Calculate the start and end time for each 24-hour window
    rolling_data['AdmTimeHourlyBegin'] = rolling_data['AdmTime'] + pd.to_timedelta(rolling_data['hr'], unit='h')
    rolling_data['AdmTimeHourlyFinal'] = rolling_data['AdmTimeHourlyBegin'] + pd.Timedelta(hours=24)

    # Adjust the upper limit to not exceed the outcome date
    rolling_data['AdmTimeHourlyFinal'] = np.where(
        rolling_data['AdmTimeHourlyFinal'] > rolling_data[outcome_date_col],
        rolling_data[outcome_date_col],
        rolling_data['AdmTimeHourlyFinal']
    )

    # Drop unnecessary columns if desired
    rolling_data.drop(columns=['AdmTime', outcome_date_col], inplace=True)

    # Return the expanded DataFrame sorted by PatientID and hour
    return rolling_data[["PatientID", "hr", "AdmTimeHourlyBegin", "AdmTimeHourlyFinal"]].sort_values(['PatientID', 'hr'], ascending=True)