import pandas as pd
import plotly.graph_objects as go
import numpy as np
import plotly.colors as pc

def get_sankey_viz(data: pd.DataFrame,
                   country: str = "World",
                   year_start: int = 1960,
                   year_end: int = 2020,
                   metrics: list = ['Deaths', 'Damages', 'Affected'],
                   use_log: bool = True) -> go.Figure:
    """
    Generates a colorful Sankey diagram linking disaster types to selected metrics.

    Parameters:
    - data (pd.DataFrame): Input dataframe with disaster data.
    - country (str): Country to filter; 'World' for global.
    - year_start (int): Start year.
    - year_end (int): End year.
    - metrics (list): Metrics to include.
    - use_log (bool): Whether to apply log scaling to values.

    Returns:
    - Plotly Sankey figure.
    """
    try:
        # Filter data
        df_filtered = data[(data['Year'] >= year_start) & (data['Year'] <= year_end)]
        if country != 'World':
            df_filtered = df_filtered[df_filtered['Country name'] == country]

        # Aggregate
        agg_df = df_filtered.groupby('Disaster Type')[metrics].sum().reset_index()
        disaster_types = agg_df['Disaster Type'].tolist()

        # Build source-target lists
        sources = []
        targets = []
        values = []
        link_colors = []

        # Create a color palette
        palette = pc.qualitative.Plotly  # 10 distinct colors

        # Assign a unique color for each disaster type
        type_to_color = {dt: palette[i % len(palette)] for i, dt in enumerate(disaster_types)}

        for i, dt in enumerate(disaster_types):
            for j, metric in enumerate(metrics):
                val = agg_df.loc[agg_df['Disaster Type'] == dt, metric].values[0]
                
                if use_log:
                    val_scaled = np.log1p(val)
                else:
                    val_scaled = val
                
                if val_scaled > 0:
                    sources.append(i)
                    targets.append(len(disaster_types) + j)
                    values.append(val_scaled)
                    link_colors.append(type_to_color[dt])

        # Labels
        labels = disaster_types + metrics

        # Sankey figure
        fig = go.Figure(go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color="lightgray"  # Node color
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=link_colors,
                hovertemplate='Source: %{source.label}<br>Target: %{target.label}<br>Value (scaled): %{value:.2f}'
            )
        ))

        fig.update_layout(
            title_text=f"Sankey: Disaster Types → Metrics ({country}, {year_start}-{year_end})",
            font_size=12,
            margin=dict(t=50, l=20, r=20, b=20)
        )
        return fig

    except Exception as e:
        print(f"Error creating Sankey plot: {str(e)}")
        return go.Figure()

