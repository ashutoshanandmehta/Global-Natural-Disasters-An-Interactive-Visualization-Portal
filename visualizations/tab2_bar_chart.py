
import pandas as pd
import plotly.express as px

def get_bar_viz(data: pd.DataFrame, year: str = "2024") -> px.bar:
    """
    Creates a bar chart for GDP contributions by category for a given year.

    Parameters:
    - data (pd.DataFrame): A DataFrame with columns 'category', 'value', 'year'.
    - year (str): The year to filter the data (default: '2024').

    Returns:
    - A Plotly bar figure.
    """
    try:
        # Validate required columns
        required_columns = ['category', 'value', 'year']
        if not all(col in data.columns for col in required_columns):
            raise ValueError("DataFrame must have 'category', 'value', and 'year' columns.")
        
        # Validate value column is numerical
        if not pd.api.types.is_numeric_dtype(data['value']):
            raise ValueError("The 'value' column must be numerical.")

        # Filter data for the selected year
        filtered_data = data[data['year'] == year]

        # Create the bar chart
        fig = px.bar(
            filtered_data,
            x='category',
            y='value',
            title=f"GDP Contributions by Sector ({year})",
            labels={'value': 'GDP (Billions USD)', 'category': 'Sector'},
            color='category'
        )

        # Update layout
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Sector",
            yaxis_title="GDP (Billions USD)",
            showlegend=False,
            margin=dict(t=50, l=25, r=25, b=25)
        )

        return fig

    except Exception as e:
        print(f"Error creating bar chart: {str(e)}")
        return px.bar()  # Return an empty figure if there's an error

# Example usage for testing
if __name__ == "__main__":
    # Sample data
    sample_data = pd.DataFrame({
        'category': ['Agriculture', 'Industry', 'Services', 'Agriculture', 'Industry', 'Services'],
        'value': [100, 240, 310, 110, 260, 330],
        'year': ['2023', '2023', '2023', '2024', '2024', '2024']
    })
    fig = get_bar_viz(sample_data, year="2024")
    fig.show()
