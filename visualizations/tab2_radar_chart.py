import pandas as pd
import plotly.express as px

def get_radar_viz(
    data: pd.DataFrame,
    country: str = "World",
    year_start: int = 1960,
    year_end: int = 2020
) -> px.line_polar:
    """
    Generates an interactive radar (polar) chart of normalized metrics per disaster type,
    with true values shown on hover.

    Parameters:
    - data (pd.DataFrame): Disaster data including 'Country name', 'Year', 'Disaster Type', and metrics columns.
    - country (str): Selected country ('World' to include all).
    - year_start (int): Start year of analysis.
    - year_end (int): End year of analysis.

    Returns:
    - Plotly radar chart figure.
    """
    try:
        metrics = ['Deaths', 'Injuries', 'Damages', 'Affected', 'Assistance', 'Rendered homeless']

        # Filter data
        df_filtered = data[(data['Year'] >= year_start) & (data['Year'] <= year_end)]
        if country != 'World':
            df_filtered = df_filtered[df_filtered['Country name'] == country]

        # Aggregate
        agg_df = df_filtered.groupby('Disaster Type')[metrics].sum().reset_index()

        # Original values (melted)
        df_melt_original = agg_df.melt(id_vars='Disaster Type', var_name='Metric', value_name='True_Value')

        # Normalize
        df_norm = agg_df.copy()
        for metric in metrics:
            min_val = df_norm[metric].min()
            max_val = df_norm[metric].max()
            if max_val - min_val > 0:
                df_norm[metric] = (df_norm[metric] - min_val) / (max_val - min_val)
            else:
                df_norm[metric] = 0

        df_melt_norm = df_norm.melt(id_vars='Disaster Type', var_name='Metric', value_name='Normalized_Value')

        # Merge
        df_melt = df_melt_norm.merge(df_melt_original, on=['Disaster Type', 'Metric'])

        # Custom hover text
        df_melt['hover_text'] = (
            "Disaster: " + df_melt['Disaster Type'] +
            "<br>Metric: " + df_melt['Metric'] +
            "<br>True Value: " + df_melt['True_Value'].apply(lambda x: f"{x:,.0f}")
        )

        # Radar plot
        fig = px.line_polar(
            df_melt,
            r='Normalized_Value',
            theta='Metric',
            color='Disaster Type',
            line_close=True,
            markers=True,
            title=f"Radar Chart of Metrics per Disaster Type ({country}, {year_start}-{year_end})"
        )
        fig.update_traces(
            fill='toself',
            hovertemplate=df_melt['hover_text']
        )
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            margin=dict(t=60, l=30, r=30, b=30)
        )

        return fig

    except Exception as e:
        print(f"Error creating radar chart: {str(e)}")
        return px.line_polar()  # Return empty figure if error

