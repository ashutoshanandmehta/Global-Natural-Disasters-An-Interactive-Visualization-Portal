# tab1_overview.py
# Callback-driven charts for the redesigned Overview & Global Patterns tab.
# All three charts read the metric + year-range filters, per the project
# report's Tab 1 spec (choropleth, treemap, global trend line, KPI cards).

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from ui.theme import DISASTER_COLORS, SEQUENTIAL_SCALE, INK_MUTED

# UI label -> (column in chloropleth_tab1/merged_output, column in combined_disaster_data)
METRICS = {
    "deaths": ("Number of deaths from disasters", "Deaths", "Deaths"),
    "injured": ("Number of people injured from disasters", "Injuries", "People injured"),
    "affected": ("Number of total people affected by disasters", "Affected", "People affected"),
    "homeless": ("Number of people left homeless from disasters", "Rendered homeless", "People left homeless"),
    "damages": ("Total economic damages from disasters as a share of GDP", "Damages", "Economic damage (% of GDP)"),
}


# Raw dataset keys -> reader-facing names (match between system and real world)
TYPE_NAMES = {
    "Mass_Movements_Dry": "Mass movements (dry)",
    "Extreme_Temperatures": "Extreme temperatures",
}


def type_name(t):
    return TYPE_NAMES.get(t, t)


def metric_options():
    return [{"label": label, "value": key} for key, (_, _, label) in METRICS.items()]


def overview_kpis(iso_df, metric_key, year_range):
    """Headline numbers for the KPI tiles."""
    col, _, _ = METRICS[metric_key]
    y0, y1 = year_range
    d = iso_df[(iso_df["Year"] >= y0) & (iso_df["Year"] <= y1)]
    total = d[col].sum()
    countries = d.loc[d[col] > 0, "Country name"].nunique()
    by_year = d.groupby("Year")[col].sum()
    peak_year = int(by_year.idxmax()) if not by_year.empty and by_year.max() > 0 else None
    yearly_avg = by_year.mean() if not by_year.empty else 0
    return total, countries, peak_year, yearly_avg


def fmt_num(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    if v >= 1e9:
        return f"{v / 1e9:.1f} B"
    if v >= 1e6:
        return f"{v / 1e6:.1f} M"
    if v >= 1e3:
        return f"{v / 1e3:.1f} k"
    return f"{v:,.0f}"


def get_overview_choropleth(iso_df, metric_key="deaths", year_range=(1900, 2024),
                            log_scale=True):
    """World map: selected metric summed per country over the year range."""
    col, _, label = METRICS[metric_key]
    y0, y1 = year_range
    d = iso_df[(iso_df["Year"] >= y0) & (iso_df["Year"] <= y1)]
    agg = (d.groupby(["ISO_Code", "Country name"], as_index=False)[col].sum())
    agg = agg[agg[col] > 0]

    color = np.log10(agg[col] + 1) if log_scale else agg[col]
    fig = go.Figure(go.Choropleth(
        locations=agg["ISO_Code"],
        z=color,
        text=agg["Country name"],
        customdata=agg[[col]],
        colorscale=SEQUENTIAL_SCALE,
        marker_line_color="#0d0d0d",
        marker_line_width=0.4,
        colorbar=dict(
            title=dict(text=f"{label}<br>(log scale)" if log_scale else label,
                       side="right", font=dict(size=11)),
            thickness=12, len=0.75, outlinewidth=0,
            tickfont=dict(size=10, color=INK_MUTED),
        ),
        hovertemplate="<b>%{text}</b><br>" + label + ": %{customdata[0]:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True,
                 projection_type="natural earth"),
        margin=dict(l=0, r=0, t=8, b=0),
    )
    return fig


def get_overview_treemap(combined_df, metric_key="deaths", year_range=(1900, 2024)):
    """Share of the selected metric by disaster type (proportional impact)."""
    _, col, label = METRICS[metric_key]
    y0, y1 = year_range
    d = combined_df[(combined_df["Year"] >= y0) & (combined_df["Year"] <= y1)]
    agg = d.groupby("Disaster Type", as_index=False)[col].sum()
    agg = agg[agg[col] > 0]

    agg["Type"] = agg["Disaster Type"].map(type_name)
    color_map = {type_name(k): v for k, v in DISASTER_COLORS.items()}
    color_map["All disasters"] = "#242423"
    color_map["(?)"] = "#242423"
    fig = px.treemap(
        agg, path=[px.Constant("All disasters"), "Type"], values=col,
        color="Type", color_discrete_map=color_map,
    )
    fig.update_traces(
        root_color="rgba(0,0,0,0)",
        marker=dict(cornerradius=4),
        textinfo="label+percent parent",
        hovertemplate="<b>%{label}</b><br>" + label + ": %{value:,.0f}<extra></extra>",
    )
    fig.update_layout(margin=dict(l=4, r=4, t=8, b=4))
    return fig


def get_overview_trend(combined_df, metric_key="deaths", year_range=(1900, 2024)):
    """Global yearly total of the selected metric, split by disaster type."""
    _, col, label = METRICS[metric_key]
    y0, y1 = year_range
    d = combined_df[(combined_df["Year"] >= y0) & (combined_df["Year"] <= y1)]
    agg = (d.groupby(["Year", "Disaster Type"], as_index=False)[col].sum())

    fig = go.Figure()
    for dtype in sorted(agg["Disaster Type"].unique()):
        grp = agg[agg["Disaster Type"] == dtype]
        pretty = type_name(dtype)
        fig.add_trace(go.Scatter(
            x=grp["Year"], y=grp[col],
            mode="lines", name=pretty,
            line=dict(width=2, color=DISASTER_COLORS.get(dtype)),
            stackgroup="one",
            hovertemplate="%{x} · " + pretty + ": %{y:,.0f}<extra></extra>",
        ))
    fig.update_layout(
        yaxis=dict(title=label, rangemode="tozero"),
        xaxis=dict(title=None),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        hovermode="x unified",
        margin=dict(l=56, r=16, t=56, b=32),
    )
    return fig
