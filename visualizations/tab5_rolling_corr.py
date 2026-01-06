import pandas as pd
import plotly.graph_objects as go

def get_rolling_correlation_viz(
    data: pd.DataFrame,
    country: str = "World",
    disaster_type: str = "All",
    metric_x: str = "Deaths",
    metric_y: str = "Damages",
    window_size: int = 5
) -> go.Figure:
    """
    Creates an interactive Plotly line plot showing rolling correlation between two metrics over time.

    Parameters:
    - data (pd.DataFrame): Original disaster data.
    - country (str): Country to filter. If "World", use all data.
    - disaster_type (str): Disaster type to filter. If "All", use all types.
    - metric_x (str): First metric for correlation (default "Deaths").
    - metric_y (str): Second metric for correlation (default "Damages").
    - window_size (int): Rolling window size in years (default 5).

    Returns:
    - Plotly Figure object.
    """
    try:
        # Copy data
        df_filtered = data.copy()

        # Filter by country
        if country != "World":
            df_filtered = df_filtered[df_filtered['Country name'] == country]

        # Filter by disaster type
        if disaster_type != "All":
            df_filtered = df_filtered[df_filtered['Disaster Type'] == disaster_type]

        # Validate metrics
        metrics = ['Deaths', 'Injuries', 'Assistance', 'Damages', 'Affected', "Rendered homeless"]
        if metric_x not in metrics or metric_y not in metrics:
            raise ValueError(f"Metrics must be one of: {metrics}")

        # Aggregate by year
        df_agg = df_filtered.groupby('Year')[metrics].sum().reset_index()

        if df_agg.empty or len(df_agg) < window_size:
            raise ValueError("Not enough data points to compute rolling correlation.")

        # Compute rolling correlations
        rolling_corrs = []
        years = []

        for i in range(len(df_agg) - window_size + 1):
            window = df_agg.iloc[i:i + window_size]
            corr_value = window[[metric_x, metric_y]].corr().iloc[0, 1]
            rolling_corrs.append(corr_value)
            years.append(int(df_agg.iloc[i + window_size - 1]['Year']))

        # Create Plotly line plot
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=years,
            y=rolling_corrs,
            mode='lines+markers',
            line=dict(color='royalblue'),
            marker=dict(size=8),
            name=f"{metric_x} vs {metric_y}"
        ))

        # Add horizontal line at 0
        fig.add_shape(
            type="line",
            x0=min(years),
            y0=0,
            x1=max(years),
            y1=0,
            line=dict(color="gray", dash="dash")
        )

        # Set title and layout
        fig.update_layout(
            title=f"Rolling Correlation ({metric_x} vs {metric_y}) ({country}, {disaster_type})",
            xaxis_title="Year (End of Rolling Window)",
            yaxis_title="Correlation",
            yaxis=dict(range=[-1, 1]),
            hovermode="x unified",
            template="plotly_dark",
            width=900,
            height=450
        )

        return fig

    except Exception as e:
        print(f"Error creating rolling correlation plot: {str(e)}")
        return go.Figure()
