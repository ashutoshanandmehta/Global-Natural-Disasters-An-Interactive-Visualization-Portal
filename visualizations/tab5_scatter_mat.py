import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def get_scatter_matrix_viz(
    data: pd.DataFrame,
    country: str = "India",
    year_start: int = 2000,
    year_end: int = 2020,
    disaster_type: str = "All",
    metric_x: str = "Deaths",
    metric_y: str = "Damages"
) -> None:
    """
    Plots a scatter matrix (pair plot) between two metrics for a given country, time range, and disaster type.

    Parameters:
    - data (pd.DataFrame): Original disaster data.
    - country (str): Country to filter. If "World", no country filter is applied.
    - year_start (int): Start year.
    - year_end (int): End year.
    - disaster_type (str): Disaster type to filter. If "All", no disaster filter is applied.
    - metric_x (str): First metric for scatter plot.
    - metric_y (str): Second metric for scatter plot.

    Returns:
    - None (displays a seaborn pair plot).
    """
    try:
        # Filter data
        df_filtered = data.copy()
        if country != "World":
            df_filtered = df_filtered[df_filtered['Country name'] == country]
        df_filtered = df_filtered[
            (df_filtered['Year'] >= year_start) &
            (df_filtered['Year'] <= year_end)
        ]
        if disaster_type != "All":
            df_filtered = df_filtered[df_filtered['Disaster Type'] == disaster_type]

        # Group by year and aggregate
        df_yearly = df_filtered.groupby('Year').agg({
            metric_x: 'sum',
            metric_y: 'sum'
        }).reset_index()

        if df_yearly.empty:
            print("Filtered data is empty. No plot will be shown.")
            return

        # Pair plot (scatter matrix of two metrics)
        sns.pairplot(df_yearly[[metric_x, metric_y]], diag_kind='kde')
        plt.suptitle(
            f"Scatter Matrix: {metric_x} vs {metric_y}\n"
            f"{country if country != 'World' else 'World'}, {disaster_type} ({year_start}–{year_end})",
            y=1.02, fontsize=14
        )
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Error creating scatter matrix plot: {str(e)}")
