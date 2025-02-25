"""
-----------------------------------------------------
Module: imputation.py
Description: Functions for missing value imputation and outlier removal.
Author: Julen Berrueta Llona
Created: 2024-10-27
-----------------------------------------------------
"""

import pandas as pd
import numpy as np

def impute_first_row_and_forward_fill(df, group_col, imputer):
    """
    Imputes missing values only in the first row of each group and forward-fills these values
    to the remaining rows within the group, without overwriting existing values.

    Args:
    - df (pd.DataFrame): DataFrame containing missing values to be imputed.
    - group_col (str): Name of the column defining the groups (e.g., 'PatientID').
    - imputer: An imputer object (e.g., IterativeImputer) with a fitted 'transform' method to impute missing values.

    Returns:
    - pd.DataFrame: DataFrame with missing values imputed and forward-filled within each group.

    Example:
    --------
    >>> from sklearn.impute import IterativeImputer
    >>> imputer = IterativeImputer(random_state=42)
    >>> imputer.fit(df[['feature1', 'feature2']])
    >>> df_imputed = impute_first_row_and_forward_fill(df, 'PatientID', imputer)
    """

    # Identify the columns to impute, excluding metadata columns
    columns_to_impute = df.drop(['PatientID', 'hr', 'AdmTimeHourlyBegin', 'AdmTimeHourlyFinal'], axis=1).columns

    # Function to process each group
    def process_group(group):
        # Extract the first row and convert it to a DataFrame
        first_row = group.iloc[[0], :].copy()

        # Impute missing values only in the first row
        first_row.loc[:, columns_to_impute] = imputer.transform(first_row[columns_to_impute])

        # Update the group with imputed values from the first row without overwriting existing values
        group.update(first_row)

        # Forward-fill missing values within the group
        return group.fillna(method='ffill')

    # Apply the processing function to each group
    return df.groupby(group_col, group_keys=False).apply(process_group)

def remove_outliers_mad(df, column, threshold=3.5):
    """
    Removes outliers from a DataFrame column using the Median Absolute Deviation (MAD) method.

    Args:
    - df (pd.DataFrame): The input DataFrame.
    - column (str): The column name from which to remove outliers.
    - threshold (float, optional): The modified Z-score threshold to identify outliers (default is 3.5).

    Returns:
    - pd.DataFrame: A DataFrame with outliers removed from the specified column.

    Example:
    --------
    >>> df = remove_outliers_mad(df, "Value")
    """

    # Calculate the median of the specified column, ignoring NaN values
    median = np.nanmedian(df[column])

    # Calculate the Median Absolute Deviation (MAD)
    mad = np.nanmedian(np.abs(df[column] - median))

    # Compute the modified Z-scores for each data point
    modified_z_scores = 0.6745 * (df[column] - median) / mad

    # Filter the DataFrame to keep only values within the threshold
    return df[(np.abs(modified_z_scores) < threshold)]