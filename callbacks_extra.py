# callbacks_extra.py
# Callbacks for the redesigned Overview tab and the Risk Clusters (UMAP) tab.

from dash import Input, Output, callback, callback_context, no_update

from ui.components import (
    chloropleth_tab1_data, combined_disaster_data_data, umap_data,
    YEAR_MAX,
)
from ui.theme import apply_theme
from visualizations.tab1_overview import (
    METRICS, fmt_num, get_overview_choropleth, get_overview_treemap,
    get_overview_trend, overview_kpis,
)
from visualizations.tab6_umap import get_cluster_profile, get_umap_scatter

DEFAULT_METRIC = "deaths"
DEFAULT_YEARS = [1960, YEAR_MAX]


# ------------------------------------------------------------- overview -----
@callback(
    Output("ov-metric", "value"),
    Output("ov-years", "value"),
    Input("ov-reset", "n_clicks"),
    prevent_initial_call=True,
)
def reset_overview_filters(_):
    """User control & freedom: one click back to the default view."""
    return DEFAULT_METRIC, list(DEFAULT_YEARS)


@callback(
    Output("kpi-total", "children"),
    Output("kpi-avg", "children"),
    Output("kpi-countries", "children"),
    Output("kpi-peak", "children"),
    Input("ov-metric", "value"),
    Input("ov-years", "value"),
)
def update_overview_kpis(metric, years):
    metric = metric or DEFAULT_METRIC
    years = years or DEFAULT_YEARS
    total, countries, peak_year, yearly_avg = overview_kpis(
        chloropleth_tab1_data, metric, years)
    return (fmt_num(total), fmt_num(yearly_avg), f"{countries}",
            str(peak_year) if peak_year else "—")


@callback(
    Output("ov-choropleth", "figure"),
    Input("ov-metric", "value"),
    Input("ov-years", "value"),
)
def update_overview_choropleth(metric, years):
    fig = get_overview_choropleth(
        chloropleth_tab1_data, metric or DEFAULT_METRIC, years or DEFAULT_YEARS)
    return apply_theme(fig)


@callback(
    Output("ov-trend", "figure"),
    Input("ov-metric", "value"),
    Input("ov-years", "value"),
)
def update_overview_trend(metric, years):
    fig = get_overview_trend(
        combined_disaster_data_data, metric or DEFAULT_METRIC,
        years or DEFAULT_YEARS)
    return apply_theme(fig)


@callback(
    Output("ov-treemap", "figure"),
    Input("ov-metric", "value"),
    Input("ov-years", "value"),
)
def update_overview_treemap(metric, years):
    fig = get_overview_treemap(
        combined_disaster_data_data, metric or DEFAULT_METRIC,
        years or DEFAULT_YEARS)
    return apply_theme(fig)


# ------------------------------------------------------------- UMAP tab -----
@callback(
    Output("umap-year", "value"),
    Output("umap-country", "value"),
    Input("umap-reset", "n_clicks"),
    prevent_initial_call=True,
)
def reset_umap_filters(_):
    return int(umap_data["year"].max()), None


@callback(
    Output("umap-scatter", "figure"),
    Input("umap-year", "value"),
    Input("umap-country", "value"),
)
def update_umap_scatter(year, country):
    fig = get_umap_scatter(umap_data, year=year, highlight_country=country)
    return apply_theme(fig)


@callback(
    Output("umap-profile", "figure"),
    Input("umap-scatter", "clickData"),
    Input("umap-reset", "n_clicks"),
)
def update_umap_profile(click_data, _reset):
    """Click a country point on the map to profile its cluster vs. the world."""
    triggered = callback_context.triggered[0]["prop_id"].split(".")[0] \
        if callback_context.triggered else None
    cluster = None
    if triggered == "umap-scatter" and click_data and click_data.get("points"):
        cd = click_data["points"][0].get("customdata")
        if cd and len(cd) >= 6:
            cluster = cd[5]
    fig = get_cluster_profile(umap_data, cluster=cluster)
    return apply_theme(fig)
