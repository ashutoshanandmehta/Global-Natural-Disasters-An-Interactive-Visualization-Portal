import plotly.express as px
import pandas as pd

def get_pie_viz(data, country, metric, year_start, year_end):
    df_filtered = data[
        (data['Country name'] == country) &
        (data['Year'] >= year_start) &
        (data['Year'] <= year_end)
    ]
    df_agg = df_filtered.groupby('Disaster Type').agg({metric: 'sum'}).reset_index()
    df_agg[metric] = df_agg[metric].fillna(0)

    # Sort & keep only top contributing disasters (optional)
    df_agg = df_agg.sort_values(by=metric, ascending=False)
    df_agg = df_agg[df_agg[metric] > df_agg[metric].sum() * 0.01]  # >1% only

    fig = px.pie(
        df_agg,
        names='Disaster Type',
        values=metric,
        title=f"{metric} Distribution in {country} ({year_start}-{year_end})",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    fig.update_traces(
        hoverinfo='label+value+percent',
        textinfo='label+percent',
        textposition='inside',  # Labels inside slice
        textfont_size=14,
        pull=[0.08 if i == 0 else 0.04 for i in range(len(df_agg))],
        marker=dict(line=dict(color='#000000', width=1))
    )

    fig.update_layout(
        title_font_size=24,
        legend_title_text='Disaster Type',
        legend=dict(font=dict(size=12)),
        margin=dict(t=80, b=20, l=20, r=20)
    )

    return fig
