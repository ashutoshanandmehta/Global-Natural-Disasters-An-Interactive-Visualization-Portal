import plotly.express as px
import pandas as pd

def get_choropleth_viz(df: pd.DataFrame):
    fig = px.choropleth(
        df,
        locations='ISO_Code',
        color='log_damage',
        hover_name='Country name',
        animation_frame='Year',
        color_continuous_scale='Turbo',
        title='Global Disaster Impact (Log Scale): Economic Damages as % of GDP',
        range_color=(df['log_damage'].min(), df['log_damage'].max())
    )

    fig.update_layout(
        geo=dict(
    showframe=False,

    showcoastlines=True,
    projection_type='equirectangular',
    lataxis_showgrid=True,
    lonaxis_showgrid=True,
    fitbounds="locations"  # <<< This makes the map occupy more space
),
        coloraxis_colorbar=dict(
            title=dict(text='GDP Damage (%)', side='right')
        ),
        paper_bgcolor='rgba(0,0,0,0.6)',  # transparent background
plot_bgcolor='rgba(0,0,0,0.6)',   # transparent plot area
font=dict(color='white'),       # black text (title, labels, legend)

        autosize=True,
        margin=dict(l=0, r=0, t=40, b=0),  # minimal margins
        title_font_size=25
    )

    fig.update_layout(legend=dict(font=dict(size=16)))

    return fig
