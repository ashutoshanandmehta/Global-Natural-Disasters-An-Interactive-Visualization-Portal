
import pandas as pd
import plotly.express as px

def get_treemap_viz(
    data: pd.DataFrame,
    metric: str,
    country: str = "World"
) -> px.treemap:
    """
    Creates an interactive treemap visualization of disaster metrics by disaster type.

    Parameters:
    - data (pd.DataFrame): The raw disaster data DataFrame.
    - metric (str): Column name for metric to visualize (e.g., 'Deaths', 'Damages', 'Affected').
    - country (str): Country name to filter by. If 'World', use all data.

    Returns:
    - A Plotly treemap figure.
    """
    try:
        # Validate
        if metric not in data.columns:
            raise ValueError(f"'{metric}' column not found in data.")

        if 'Disaster Type' not in data.columns:
            raise ValueError("'Disaster Type' column not found in data.")

        if 'Country name' not in data.columns:
            raise ValueError("'Country name' column not found in data.")

        # Filter by country
        if country != "World":
            df_filtered = data[data['Country name'] == country].copy()
        else:
            df_filtered = data.copy()

        # Aggregate by Disaster Type
        df_agg = df_filtered.groupby('Disaster Type').agg({metric: 'sum'}).reset_index()

        # Prepare DataFrame with 'path' and 'value' columns for your logic
        df_agg['path'] = df_agg.apply(lambda row: [row['Disaster Type']], axis=1)
        df_agg = df_agg.rename(columns={metric: 'value'})

        # Check if data is empty
        if df_agg['value'].sum() == 0:
            raise ValueError("All metric values are zero for this filter.")

        # Transform path column to separate levels
        max_depth = max(len(p) for p in df_agg['path'])
        path_columns = [f'level{i+1}' for i in range(max_depth)]
        path_df = pd.DataFrame(df_agg['path'].tolist(), columns=path_columns, index=df_agg.index)
        transformed_data = pd.concat([path_df, df_agg['value']], axis=1)

        # Create treemap
        fig = px.treemap(
            transformed_data,
            path=path_columns,
            values='value',
            color='value',
            color_continuous_scale='Viridis',
            title=f"{'World' if country == 'World' else country} Distribution of {metric} by Disaster Type"
        )

        # Update layout
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=50, l=25, r=25, b=25),
            title_font_size=20,
            font=dict(family='Tektur, Segoe UI, sans-serif', color='white')
        )

        return fig

    except Exception as e:
        print(f"Error creating treemap visualization: {str(e)}")
        return px.treemap()  # Empty fallback figure

# Example usage for testing
if __name__ == "__main__":
    # Sample data
    sample_data = pd.DataFrame({
        'path': [
            ['Agriculture', 'Crops'],
            ['Agriculture', 'Livestock'],
            ['Industry', 'Manufacturing'],
            ['Services', 'IT Services']
        ],
        'value': [80, 20, 180, 150]
    })
    fig = get_treemap_viz(sample_data)
    fig.show()