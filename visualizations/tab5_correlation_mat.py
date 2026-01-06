import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def get_country_metric_correlation_viz(
    data: pd.DataFrame,
    country: str = "India",
    year_start: int = 2000,
    year_end: int = 2020,
    metrics: list = ['Deaths', 'Injuries', 'Assistance', 'Damages', 'Affected', 'Rendered homeless']
) -> None:
    """
    Plots a heatmap of correlations between selected metrics for a given country and time range.

    Parameters:
    - data (pd.DataFrame): Original disaster data.
    - country (str): Country to filter.
    - year_start (int): Start year.
    - year_end (int): End year.
    - metrics (list): List of metrics to include in the correlation heatmap.

    Returns:
    - None (displays a seaborn heatmap plot).
    """
    try:
        # Copy data
        df_filtered = data.copy()

        # Filter by country
        if country != "World":
            df_filtered = df_filtered[df_filtered['Country name'] == country]
        # Filter data
        df_country = df_filtered[
            (data['Year'] >= year_start) &
            (data['Year'] <= year_end)
        ]

        if df_country.empty:
            print("Filtered data is empty. No plot will be shown.")
            return

        # Group by year and aggregate
        df_yearly = df_country.groupby('Year').agg({
            'Deaths': 'sum',
            'Injuries': 'sum',
            'Assistance': 'sum',
            'Damages': 'mean',  # Assuming % GDP
            'Affected': 'sum',
            'Rendered homeless': 'sum'
        }).reset_index()

        # Prepare correlation matrix
        df_corr = df_yearly[metrics].fillna(0)
        corr_matrix = df_corr.corr()

        # Plot heatmap
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
        plt.title(f'Metric Correlation Over Time in {country} ({year_start}–{year_end})')
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Error creating correlation heatmap: {str(e)}")
