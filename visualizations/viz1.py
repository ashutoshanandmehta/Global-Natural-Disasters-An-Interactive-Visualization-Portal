
import pandas as pd
import plotly.express as px

def get_sunburst_viz(data: pd.DataFrame) -> px.sunburst:
    """
    Creates a sunburst visualization using the provided preprocessed data.

    Parameters:
    - data (pd.DataFrame): A DataFrame with columns 'path' (list of strings) and 'value' (numeric).

    Returns:
    - A Plotly sunburst figure.
    """
    try:
        # Validate required columns
        if 'path' not in data.columns or 'value' not in data.columns:
            raise ValueError("DataFrame must have 'path' and 'value' columns.")

        # Validate 'path' column contains lists
        if not all(isinstance(p, list) for p in data['path']):
            raise ValueError("'path' column must contain lists of strings.")

        # Validate 'value' column is numerical
        if not pd.api.types.is_numeric_dtype(data['value']):
            raise ValueError("'value' column must be numerical.")

        # Debug: Print sample data
        print("Sunburst data sample:", data.head().to_dict())

        # Transform 'path' into separate columns
        max_depth = max(len(path) for path in data['path'])
        path_columns = [f'level{i+1}' for i in range(max_depth)]
        path_df = pd.DataFrame(data['path'].tolist(), columns=path_columns, index=data.index)
        transformed_data = pd.concat([path_df, data['value']], axis=1)

        # Create the sunburst visualization
        fig = px.sunburst(
            transformed_data,
            path=path_columns,
            values='value',
            title="India's GDP Sunburst"
        )

        # Update layout
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=50, l=25, r=25, b=25),
            title_font_size=20
        )

        return fig

    except Exception as e:
        print(f"Error creating sunburst visualization: {str(e)}")
        return px.sunburst()  # Return an empty figure if there's an error

# Example usage for testing
if __name__ == "__main__":
    # Sample data
    sample_data = pd.DataFrame({
        'path': [
            ['Agriculture', 'Crops', 'Food Crops'],
            ['Agriculture', 'Crops', 'Cash Crops'],
            ['Agriculture', 'Livestock'],
            ['Industry', 'Manufacturing', 'Electronics'],
            ['Industry', 'Manufacturing', 'Textiles'],
            ['Industry', 'Construction'],
            ['Services', 'IT Services'],
            ['Services', 'Tourism'],
            ['Services', 'Finance']
        ],
        'value': [50, 30, 20, 100, 80, 60, 150, 70, 90]
    })
    fig = get_sunburst_viz(sample_data)
    fig.show()
