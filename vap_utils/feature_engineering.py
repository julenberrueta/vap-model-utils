"""
-----------------------------------------------------
Module: feature_engineering.py
Description: Functions for feature extraction and transformation.
Author: Julen Berrueta Llona
Created: 2024-10-27
-----------------------------------------------------
"""

def extract_value(pattern, x):
    """
    Extracts the first match from a string based on a given regular expression pattern.

    Args:
    - pattern (str): The regular expression pattern to search for.
    - x (str): The input string from which to extract the value.

    Returns:
    - str or int: The matched value if found; otherwise, returns -999.

    Example:
    --------
    >>> pattern = '[1-9][0-9]?'
    >>> df["Value"] = df["StringValue"].apply(lambda x: extract_value(pattern, x))
    """

    # Search for the pattern in the input string
    match = re.search(pattern, x)

    # If a match is found, return the matched value
    if match:
        return match.group()
    else:
        # Return -999 if no match is found
        return -999