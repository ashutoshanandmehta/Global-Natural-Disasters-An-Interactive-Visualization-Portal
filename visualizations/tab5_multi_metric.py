import pandas as pd
import plotly.express as px

def get_multi_metric_parallel_viz(
    data: pd.DataFrame,
    country: str = "World",
    disaster_type: str = "All",
    metrics: list = ['Deaths', 'Injuries', 'Assistance', 'Damages', 'Affected', "Rendered homeless"]
) -> px.parallel_coordinates:
    """
    Creates an interactive parallel coordinates plot to compare multiple metrics over years.

    Parameters:
    - data (pd.DataFrame): Original disaster data.
    - country (str): Country to filter. If "World", uses all countries.
    - disaster_type (str): Disaster type to filter. If "All", uses all types.
    - metrics (list): List of metrics to include.

    Returns:
    - Plotly parallel coordinates figure.
    """
    try:
        # Filter data
        df_filtered = data.copy()
        if country != "World":
            df_filtered = df_filtered[df_filtered['Country name'] == country]
        if disaster_type != "All":
            df_filtered = df_filtered[df_filtered['Disaster Type'] == disaster_type]

        # Aggregate by year
        df_agg = df_filtered.groupby('Year')[metrics].sum().reset_index()

        if df_agg.empty:
            raise ValueError("Filtered data is empty. Cannot plot.")

        # Normalize columns
        df_norm = df_agg.copy()
        for metric in metrics:
            min_val = df_norm[metric].min()
            max_val = df_norm[metric].max()
            if max_val - min_val > 0:
                df_norm[metric] = (df_norm[metric] - min_val) / (max_val - min_val)
            else:
                df_norm[metric] = 0  # In case of constant column

        # Create parallel coordinates plot
        fig = px.parallel_coordinates(
            df_norm,
            dimensions=metrics,
            color='Year',
            title=f"Multi-Metric Parallel Coordinates ({country if country != 'World' else 'World'}, {disaster_type})",
            color_continuous_scale=px.colors.sequential.Viridis
        )

        # Optional: Style adjustments (Plotly parallel_coordinates does not support detailed hover text yet)
        fig.update_layout(
            title_font_size=20,
            width=1000,
            height=500,
            template="plotly_dark"
        )

        return fig

    except Exception as e:
        print(f"Error creating parallel coordinates plot: {str(e)}")
        return px.parallel_coordinates(pd.DataFrame({'Empty': []}), dimensions=['Empty'])  # Return empty figure if error
