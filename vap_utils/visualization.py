"""
-----------------------------------------------------
Module: patient_probability_plot.py
Description: Functions to visualize patient probabilities with color-coded segments 
             and key event markers (e.g., NAV events, VMI periods).
Author: Julen Berrueta Llona
Created: 2024-10-27
-----------------------------------------------------
"""

import pandas as pd
import plotly.graph_objects as go

def assign_color(prob):
    """
    Assigns a pastel color based on the probability value.

    Args:
    - prob (float): The probability value ranging between 0 and 1.

    Returns:
    - str: Hex color code representing the assigned color.

    Color mapping:
    - [0, 0.25): Light pastel green
    - [0.25, 0.4): Light pastel yellow
    - [0.4, 0.5): Light pastel orange
    - [0.5, 1]: Light pastel red
    - Default: Light grey
    """
    if 0 <= prob < 0.25:
        return "#97ed95"  # Light pastel green
    elif 0.25 <= prob < 0.4:
        return "#fff4c3"  # Light pastel yellow
    elif 0.4 <= prob < 0.5:
        return "#ffd1a1"  # Light pastel orange
    elif prob >= 0.5:
        return "#f6b2b0"  # Light pastel red
    else:
        return "#d9d9d9"  # Default neutral grey

def plot_patient_probability(df, patient_id, NAV, ultima_VMI=None, primera_VMI=None):
    """
    Plots patient probability over time with color-coded segments based on probability ranges.
    It highlights NAV events and their 24-hour pre-events, and draws a line indicating the VMI period.

    Args:
    - df (pd.DataFrame): DataFrame containing ['PatientID', 'prob', 'AdmTimeHourlyFinal'].
                         Represents the time series of probabilities for all patients.
    - patient_id (int): The specific PatientID to visualize.
    - NAV (pd.DataFrame): DataFrame with ['PatientID', 'fecha_NAV'] representing NAV event dates.
    - ultima_VMI (pd.DataFrame): DataFrame with ['PatientID', 'last_VMI'] for last VMI event.
    - primera_VMI (pd.DataFrame): DataFrame with ['PatientID', 'first_VMI'] for first VMI event.

    Returns:
    - None: Displays an interactive Plotly chart.

    Example:
    --------
    >>> import pandas as pd
    >>> from datetime import datetime, timedelta

    # Sample DataFrame for probabilities
    >>> df = pd.DataFrame({
    ...     'PatientID': [101]*10,
    ...     'prob': [0.1, 0.2, 0.65, 0.75, 0.45, 0.55, 0.4, 0.3, 0.2, 0.2],
    ...     'AdmTimeHourlyFinal': [datetime(2024, 10, 1) + timedelta(days=i) for i in range(10)]
    ... })

    # NAV events DataFrame
    >>> NAV = pd.DataFrame({
    ...     'PatientID': [101],
    ...     'fecha_NAV': [datetime(2024, 10, 4)]
    ... })

    # VMI period DataFrames
    >>> primera_VMI = pd.DataFrame({
    ...     'PatientID': [101],
    ...     'first_VMI': [datetime(2024, 10, 1)]
    ... })

    >>> ultima_VMI = pd.DataFrame({
    ...     'PatientID': [101],
    ...     'last_VMI': [datetime(2024, 10, 9)]
    ... })

    # Plot the patient probability chart
    >>> plot_patient_probability(df, patient_id=101, NAV=NAV, ultima_VMI=ultima_VMI, primera_VMI=primera_VMI)
    """

    # Filter the main DataFrame for the selected patient
    patient_df = df[df['PatientID'] == patient_id].copy()

    # Assign colors to each probability based on its range
    patient_df['color'] = patient_df['prob'].apply(assign_color)

    # Filter NAV, first VMI, and last VMI DataFrames for the specific patient
    nav_df = NAV[NAV['PatientID'] == patient_id]

    # Initialize Plotly figure
    fig = go.Figure()

    # Add a horizontal line at y=0.5 to mark a threshold
    fig.add_hline(y=0.5, line_width=1, line_dash="solid", line_color="gray", name="Threshold 0.5")

    # Extract x-axis (time) and y-axis (probabilities)
    x_vals = patient_df['AdmTimeHourlyFinal'].values
    y_vals = patient_df['prob'].values
    color = patient_df['color'].values

    # Plot probability segments with assigned colors
    for i in range(1, len(x_vals)):
        fig.add_trace(go.Scatter(
            x=x_vals[i-1:i+1],  # Two consecutive points for a line segment
            y=y_vals[i-1:i+1],
            mode='lines',
            line=dict(color=color[i], width=3),  # Use color mapping
            showlegend=False  # Do not show individual line segments in the legend
        ))

    # Flags to ensure only one legend entry for NAV markers
    first_nav = True
    first_24h = True

    # Plot NAV event markers and 24-hour pre-event markers
    if not nav_df.empty:
        for _, row in nav_df.iterrows():
            fecha_nav = row['fecha_NAV']
            # Find the closest timestamp <= fecha_NAV
            fecha_nav = pd.to_datetime(patient_df.loc[patient_df['AdmTimeHourlyFinal'] <= fecha_nav, 'AdmTimeHourlyFinal'].values[-1])
            fecha_24h = fecha_nav - pd.Timedelta(days=1)

            # Get probability values at NAV and 24 hours before NAV
            prob_nav = patient_df.loc[patient_df['AdmTimeHourlyFinal'] <= fecha_nav, 'prob'].values
            prob_24h = patient_df.loc[patient_df['AdmTimeHourlyFinal'] <= fecha_24h, 'prob'].values

            # Plot NAV marker (red)
            if prob_nav.size > 0:
                fig.add_trace(go.Scatter(
                    x=[fecha_nav],
                    y=[prob_nav[-1]],
                    mode='markers',
                    marker=dict(color='#fa8373', size=10),
                    name="NAV" if first_nav else None,
                    showlegend=first_nav
                ))
                first_nav = False

            # Plot 24h pre-NAV marker (green)
            if prob_24h.size > 0:
                fig.add_trace(go.Scatter(
                    x=[fecha_24h],
                    y=[prob_24h[-1]],
                    mode='markers',
                    marker=dict(color='#79e067', size=10),
                    name="24h Before NAV" if first_24h else None,
                    showlegend=first_24h
                ))
                first_24h = False

    # Plot VMI period as a horizontal line at y=0
    if primera_VMI is not None and ultima_VMI is not None:
        ultima_VMI = ultima_VMI[ultima_VMI['PatientID'] == patient_id]
        primera_VMI = primera_VMI[primera_VMI['PatientID'] == patient_id]
        fecha_primera_VMI = primera_VMI["first_VMI"].iloc[0]
        fecha_ultima_VMI = ultima_VMI["last_VMI"].iloc[0]
        fig.add_trace(go.Scatter(
            x=[fecha_primera_VMI, fecha_ultima_VMI],
            y=[0, 0],
            mode='lines',
            line=dict(color='#99bbff', width=2, dash='solid'),
            name="VMI Period"
        ))

    # Update chart layout and aesthetics
    fig.update_layout(
        title=f'Probabilities for PatientID {patient_id} with Color Coding',
        xaxis_title='Time (AdmTimeHourlyFinal)',
        yaxis_title='Probability',
        showlegend=True,
        legend=dict(
            x=0.85,
            y=0.99,
            bgcolor='rgba(255, 255, 255, 0.5)',
        ),
        yaxis=dict(
            range=[-0.05, 1.05],
            tick0=0,
            dtick=0.2
        ),
        xaxis=dict(
            tickformat='%d/%m/%Y'  # Format x-axis as dates
        ),
        height=400
    )

    # Display the Plotly chart
    fig.show()
