# components.py
# Layout for every tab. Design rules:
#   - one ChartCard pattern everywhere (consistency & standards)
#   - one ControlBar per tab, filters always visible (recognition over recall)
#   - dcc.Loading on every callback-driven graph (visibility of system status)
#   - failed charts render a visible error card, never a fake skeleton
#     (help users recognize, diagnose, and recover from errors)

from pathlib import Path

import pandas as pd
from dash import html, dcc

from utils.data_loader import load_all_csvs
from .theme import (
    ChartCard, ControlBar, ErrorCard, Field, InfoTip, KpiTile, LoadedGraph,
    SafeFigure, apply_theme,
)

from visualizations.tab1_overview import metric_options
from visualizations.tab2_stacked_area import plot_stacked_disasters_by_year
from visualizations.tab2_sankey import get_sankey_viz
from visualizations.tab2_radar_chart import get_radar_viz
from visualizations.tab3_scatter import get_scatter_plot3
from visualizations.tab3_bubble import get_bubble_viz_tab3
from visualizations.tab3_area import get_area_chart3
from visualizations.tab3_lolli import get_lollipop3
from visualizations.tab5_correlation_mat import get_country_metric_correlation_viz
from visualizations.tab5_correlation_net import get_disaster_network_viz
from visualizations.tab5_multi_metric import get_multi_metric_parallel_viz
from visualizations.tab5_rolling_corr import get_rolling_correlation_viz
from visualizations.tab5_scatter_mat import get_scatter_matrix_viz
from visualizations.tab6_umap import load_embedding

# ------------------------------------------------------------------ data ----
_ROOT = Path(__file__).resolve().parent.parent
_processed = load_all_csvs(_ROOT / "data" / "processed")

chloropleth_tab1_data = _processed["chloropleth_tab1_data"]
combined_disaster_data_data = _processed["combined_disaster_data_data"]
merged_output_data = _processed["merged_output_data"]
tab3_scatter_data = _processed["tab3_scatter_data"]
tab3_bubble_data = _processed["tab3_bubble_data"]
tab3_area_data = _processed["tab3_area_data"]
tab3_lolli_data = _processed["tab3_lolli_data"]

main_data = pd.read_csv(_ROOT / "data" / "Risk_Analysis" / "final_risk_merged.csv")
umap_data = load_embedding()

YEAR_MIN = int(chloropleth_tab1_data["Year"].min())
YEAR_MAX = int(chloropleth_tab1_data["Year"].max())
UMAP_YEARS = sorted(umap_data["year"].unique())
UMAP_COUNTRIES = sorted(umap_data["country"].unique())

# ---------------------------------------------------------------- chrome ----
Topbar = html.Header(className="topbar", children=[
    html.Div(className="topbar__brand", children=[
        html.Span("Global Natural Disasters", className="topbar__title"),
        html.Span("Interactive Visualization Portal", className="topbar__subtitle"),
    ]),
    # Signature: a quiet seismograph trace running across the top bar
    html.Div(className="topbar__trace", **{"aria-hidden": "true"}),
    html.Div(className="theme-toggle theme-toggle--dark", id="theme-toggle",
             role="button", tabIndex=0, title="Switch light / dark theme",
             children=[html.Div(className="theme-toggle__ball")]),
])

tabs = [
    ("overview", "fa-solid fa-earth-asia", "Overview & Global Patterns"),
    ("disaster-analysis", "fa-solid fa-bolt", "Disaster Type Analysis"),
    ("economic-impact", "fa-solid fa-coins", "Economic Impact & Vulnerability"),
    ("country-profiles", "fa-solid fa-magnifying-glass-chart", "Country Risk Profiles"),
    ("risk-clusters", "fa-solid fa-circle-nodes", "Risk Clusters (UMAP)"),
    ("trends-correlations", "fa-solid fa-chart-line", "Trends & Correlations"),
    ("data-sources", "fa-solid fa-database", "Data & Sources"),
]

SidebarTabs = html.Nav(className="sidebar-tabs", children=[
    html.Div(className="sidebar-tabs__eyebrow", children="Explore"),
    *[
        html.Div(
            className=f"sidebar-tab {'sidebar-tab--active' if key == 'overview' else ''}",
            role="button", tabIndex=0,
            **{"data-tab": key},
            children=[
                html.I(className=f"icon {icon}", **{"aria-hidden": "true"}),
                html.Span(label, className="tab-label"),
            ],
        )
        for key, icon, label in tabs
    ],
])

Sidebar = html.Aside(id="sidebar", className="sidebar", children=[
    html.Button(id="sidebar-toggle", className="sidebar-toggle",
                title="Collapse sidebar", children=[
        html.Span(className="bar"), html.Span(className="bar"),
        html.Span(className="bar"),
    ]),
    SidebarTabs,
    html.Div(className="sidebar__foot",
             children="CS661 · Group 16 · IIT Kanpur"),
])


# --------------------------------------------------------------- tab 1 ------
def overview_tab():
    slider_marks = {y: str(y) for y in range(YEAR_MIN - YEAR_MIN % 20 + 20,
                                             YEAR_MAX + 1, 20)}
    return [
        ControlBar([
            Field("Impact metric", dcc.Dropdown(
                id="ov-metric", options=metric_options(), value="deaths",
                clearable=False, className="dd", style={"width": "260px"},
            )),
            Field("Years", html.Div(dcc.RangeSlider(
                id="ov-years", min=YEAR_MIN, max=YEAR_MAX,
                value=[1960, YEAR_MAX], marks=slider_marks,
                tooltip={"placement": "bottom", "always_visible": False},
                allowCross=False,
            ), className="control-bar__slider")),
            html.Button("Reset filters", id="ov-reset", className="btn-ghost",
                        title="Back to Deaths · 1960 onwards"),
        ]),
        html.Div(className="kpi-row", children=[
            KpiTile("kpi-total", "Total (selected metric)", "selected years"),
            KpiTile("kpi-avg", "Yearly average", "selected years"),
            KpiTile("kpi-countries", "Countries affected", "with impact > 0"),
            KpiTile("kpi-peak", "Worst year", "highest global total"),
        ]),
        html.Div(className="tab-grid", children=[
            ChartCard(
                "Where disasters hit hardest", span=12,
                subtitle="Selected metric, summed per country over the selected years (log color scale)",
                info="Darker countries carry a larger share of the selected impact "
                     "metric. Hover a country for its exact total. Use the year "
                     "slider above to change the period.",
                children=LoadedGraph("ov-choropleth", height="480px"),
            ),
            ChartCard(
                "Global trend over time", span=7,
                subtitle="Yearly world total, stacked by disaster type",
                info="Each band is one disaster type; the top edge is the world "
                     "total for that year. Hover a year to compare types.",
                children=LoadedGraph("ov-trend", height="380px"),
            ),
            ChartCard(
                "Share by disaster type", span=5,
                subtitle="Proportional impact for the selected metric and years",
                info="Rectangle area is proportional to each disaster type's share "
                     "of the selected metric. Click a rectangle to zoom in.",
                children=LoadedGraph("ov-treemap", height="380px"),
            ),
        ]),
    ]


# --------------------------------------------------------------- tab 2 ------
def disaster_analysis_tab():
    stacked_fig = apply_theme(plot_stacked_disasters_by_year(main_data))
    return [
        ControlBar([], note="Recorded disaster events (EM-DAT), 2000–2024. "
                            "Hover any chart for exact values."),
        html.Div(className="tab-grid", children=[
            ChartCard(
                "Events per year, by disaster type", span=12,
                subtitle="Count of recorded events, stacked by type",
                info="Bar height is the number of recorded disaster events that "
                     "started in that year; colors split the total by type.",
                children=dcc.Graph(
                    id="tab2_bar_chart", figure=stacked_fig,
                    config={"displayModeBar": False, "responsive": True},
                    clear_on_unhover=True, style={"height": "420px"},
                ),
            ),
            SafeFigure(
                get_sankey_viz, main_data,
                title="From hazard to human impact",
                subtitle="Flows from disaster types to deaths, damages and people affected",
                info="Ribbon width is proportional to impact (log-scaled). Follow "
                     "a ribbon from a disaster type on the left to its impact "
                     "on the right.",
                span=6, height="480px",
            ),
            SafeFigure(
                get_radar_viz, combined_disaster_data_data,
                title="Impact profile per disaster type",
                subtitle="Normalized metric signature, world · 1999–2020",
                info="Each polygon is one disaster type; each axis is one impact "
                     "metric normalized to 0–1, so shapes compare the *profile* "
                     "of harm, not absolute size. Hover vertices for true values.",
                span=6, height="480px",
            ),
        ]),
    ]


# --------------------------------------------------------------- tab 3 ------
def economic_impact_tab():
    return [
        ControlBar([], note="Economic losses in context: what damage means "
                            "relative to the size of each economy."),
        html.Div(className="tab-grid", children=[
            SafeFigure(
                get_scatter_plot3, tab3_scatter_data,
                title="Wealth vs. relative damage",
                subtitle="GDP per capita against damages as a share of GDP",
                info="Each point is a country. Poorer countries cluster toward "
                     "larger relative losses — the core vulnerability finding.",
                span=6, height="440px",
            ),
            SafeFigure(
                get_bubble_viz_tab3, tab3_bubble_data,
                title="Human cost, economic cost, and size",
                subtitle="Bubble area encodes a third dimension",
                info="Compare deaths against damages while bubble size shows "
                     "scale; hover for the country behind each bubble.",
                span=6, height="440px",
            ),
            SafeFigure(
                get_area_chart3, tab3_area_data,
                title="Economic losses over time",
                subtitle="Yearly losses, stacked by disaster type",
                info="Growth of a band means that disaster type's economic "
                     "burden is rising.",
                span=12, height="420px",
            ),
            SafeFigure(
                get_lollipop3, tab3_lolli_data,
                title="Most economically vulnerable countries",
                subtitle="Ranked by losses as a share of GDP · use the decade buttons inside the chart",
                info="A long stem means disasters cost that country a large "
                     "fraction of its economy, regardless of absolute size.",
                span=12, height="900px",
            ),
        ]),
    ]


# --------------------------------------------------------------- tab 4 ------
def country_profiles_tab():
    return [
        ControlBar([
            Field("Country", dcc.Dropdown(
                id="country-selector", placeholder="Choose a country…",
                className="dd", style={"width": "240px"},
            )),
            Field("Year", dcc.Dropdown(
                id="year-selector", options=[], placeholder="Choose a year…",
                className="dd", style={"width": "150px"},
            )),
            Field("Map style", dcc.Dropdown(
                id="map-style-selector",
                options=[
                    {"label": "Open Street Map", "value": "open-street-map"},
                    {"label": "Carto Positron", "value": "carto-positron"},
                    {"label": "Carto Dark Matter", "value": "carto-darkmatter"},
                ],
                value="carto-darkmatter", clearable=False,
                className="dd", style={"width": "190px"},
            )),
        ], note="Everything on this tab follows the selected country."),
        html.Div(className="tab-grid", children=[
            # Metrics card — click a map point for event details
            html.Section(className="card", style={"gridColumn": "span 4"},
                         children=[
                html.Header(className="card__header", children=[
                    html.Div(className="card__heading", children=[
                        html.H3("Country fact sheet", className="card__title"),
                        html.P("Click a dot on the map for event details; ↺ returns "
                               "to the country summary", className="card__subtitle"),
                    ]),
                    html.Div(className="card__header-right", children=[
                        html.Button("↺", id="reset-metrics-btn",
                                    className="btn-icon",
                                    title="Back to country summary"),
                    ]),
                ]),
                dcc.Store(id="click-state", data={"show_disaster": False}),
                html.Div(id="metrics-card", className="metrics-scroll"),
            ]),
            ChartCard(
                "Disaster events map", span=8,
                subtitle="Every recorded event for the selected country and year",
                info="Each dot is one recorded disaster event. Click a dot to load "
                     "its details into the fact sheet on the left.",
                children=LoadedGraph("region-hotspot-map", height="520px"),
            ),
            ChartCard(
                "Risk dimensions over time", span=6,
                subtitle="World Risk Index components, animated by year",
                info="The spider outline shows the country's score on each risk "
                     "dimension. Add countries to compare their shapes.",
                controls=dcc.Dropdown(
                    id="multi-country-selector", multi=True,
                    placeholder="Compare countries…",
                    className="dd dd--wide",
                ),
                children=LoadedGraph("country-risk-radar", height="480px"),
            ),
            html.Section(className="card", style={"gridColumn": "span 6"},
                         children=[
                html.Header(className="card__header", children=[
                    html.Div(className="card__heading", children=[
                        html.H3("Countries with a similar risk profile",
                                className="card__title"),
                        html.P(id="cluster-chlorepath-title",
                               className="card__subtitle"),
                    ]),
                    html.Div(className="card__header-right", children=[
                        InfoTip("Countries sharing the selected country's K-Means "
                                "risk cluster are shaded. Use the year slider "
                                "inside the chart to move through time."),
                    ]),
                ]),
                html.Div(className="card__body",
                         children=LoadedGraph("economic-bubble-chart",
                                              height="480px")),
            ]),
            html.Section(className="card", style={"gridColumn": "span 8"},
                         children=[
                html.Header(className="card__header", children=[
                    html.Div(className="card__heading", children=[
                        html.H3(id="parallel-plot-title",
                                children="Parallel coordinates",
                                className="card__title"),
                        html.P("Each line is one disaster event for the country",
                               className="card__subtitle"),
                    ]),
                    html.Div(className="card__header-right", children=[
                        dcc.Dropdown(
                            id="parallel-plot-type-selector",
                            options=[
                                {"label": "Risk vs Outcome", "value": "risk_vs_outcome"},
                                {"label": "Wealth vs Impact", "value": "wealth_vs_impact"},
                                {"label": "Vulnerability Path", "value": "vulnerability_path"},
                            ],
                            value="risk_vs_outcome", clearable=False,
                            className="dd", style={"width": "210px"},
                        ),
                        InfoTip("Drag along an axis to filter lines; drag an axis "
                                "title to reorder. Pick a lens from the dropdown."),
                    ]),
                ]),
                html.Div(className="card__body",
                         children=LoadedGraph("tab4-parallel-plot",
                                              height="460px")),
            ]),
            ChartCard(
                "Where events strike", span=4,
                subtitle="Locations named most often in event records",
                info="Generated from the location field of the country's disaster "
                     "records — bigger words appear more often.",
                children=html.Img(id="wordcloud-img", className="wordcloud-img",
                                  alt="Word cloud of most affected locations"),
            ),
        ]),
    ]


# --------------------------------------------------------------- tab 5 ------
def risk_clusters_tab():
    return [
        ControlBar([
            Field("Year", dcc.Dropdown(
                id="umap-year",
                options=([{"label": "All years (trajectories)", "value": "all"}] +
                         [{"label": str(y), "value": int(y)} for y in UMAP_YEARS]),
                value=int(UMAP_YEARS[-1]), clearable=False,
                className="dd", style={"width": "190px"},
            )),
            Field("Highlight country", dcc.Dropdown(
                id="umap-country",
                options=[{"label": c, "value": c} for c in UMAP_COUNTRIES],
                placeholder="Type a country…",
                className="dd", style={"width": "240px"},
            )),
            html.Button("Reset view", id="umap-reset", className="btn-ghost",
                        title="All years, no highlight"),
        ]),
        # How the map was made — help & documentation, right where it's needed
        html.Div(className="method-strip", children=[
            html.Div(className="method-step", children=[
                html.Span("1", className="method-step__n"),
                html.Div([
                    html.Strong("~50 risk indicators"),
                    html.P("World Risk Index metrics per country-year: exposure, "
                           "vulnerability, susceptibility, coping & adaptation"),
                ]),
            ]),
            html.Div("→", className="method-arrow", **{"aria-hidden": "true"}),
            html.Div(className="method-step", children=[
                html.Span("2", className="method-step__n"),
                html.Div([
                    html.Strong("Standardize"),
                    html.P("Each indicator scaled to zero mean and unit variance "
                           "so no single metric dominates"),
                ]),
            ]),
            html.Div("→", className="method-arrow", **{"aria-hidden": "true"}),
            html.Div(className="method-step", children=[
                html.Span("3", className="method-step__n"),
                html.Div([
                    html.Strong("UMAP → 2D"),
                    html.P("Neighbors-preserving projection (n_neighbors 15, "
                           "min_dist 0.1): nearby points had similar risk profiles "
                           "in the full ~50-dimensional space"),
                ]),
            ]),
            html.Div("→", className="method-arrow", **{"aria-hidden": "true"}),
            html.Div(className="method-step", children=[
                html.Span("4", className="method-step__n"),
                html.Div([
                    html.Strong("K-Means clusters"),
                    html.P("Seven groups of countries with similar socio-economic "
                           "and hazard-exposure signatures, colored below"),
                ]),
            ]),
        ]),
        html.Div(className="tab-grid", children=[
            ChartCard(
                "The risk landscape, flattened to two dimensions", span=8,
                subtitle="One point per country-year · distance means similarity of risk profile",
                info="Points close together are countries whose ~50 risk "
                     "indicators look alike — even when they sit on different "
                     "continents. Axes have no physical unit; only relative "
                     "distance matters. Click a point to profile its cluster "
                     "on the right. Scroll to zoom, drag to pan.",
                children=LoadedGraph("umap-scatter", height="560px"),
            ),
            ChartCard(
                "What defines each cluster", span=4,
                subtitle="Mean World Risk Index dimensions · click a point on the map to focus its cluster",
                info="Bars show each cluster's average score per risk dimension. "
                     "After clicking a point, the focused cluster is compared "
                     "against the global mean (gray).",
                children=LoadedGraph("umap-profile", height="560px"),
            ),
            ChartCard(
                "How to read this", span=12,
                children=html.Div(className="prose", children=[
                    html.P([
                        "UMAP (Uniform Manifold Approximation and Projection) keeps ",
                        html.Em("neighborhoods"), " intact: countries that were near "
                        "each other in the full high-dimensional risk space stay "
                        "near each other on this 2-D map. Tight islands are groups "
                        "of country-years with almost identical risk signatures; "
                        "long bridges show gradual transitions between profiles.",
                    ]),
                    html.P([
                        "Try highlighting a country to trace its 2000–2024 "
                        "trajectory: a country drifting between clusters is "
                        "changing its risk profile over time — for example, "
                        "reducing vulnerability while exposure stays constant. "
                        "India, for instance, forms a compact multi-year cluster, "
                        "meaning a persistent national risk signature.",
                    ]),
                ]),
            ),
        ]),
    ]


# --------------------------------------------------------------- tab 6 ------
def trends_correlations_tab():
    return [
        ControlBar([], note="Statistical relationships between impact metrics — "
                            "correlation is not causation."),
        html.Div(className="tab-grid", children=[
            SafeFigure(
                get_country_metric_correlation_viz, combined_disaster_data_data,
                title="Which impacts move together",
                subtitle="Pairwise correlation between impact metrics",
                info="Red cells: the two metrics rise together; blue: one rises "
                     "as the other falls. Values near 0 mean no linear link.",
                span=6, height="460px",
            ),
            SafeFigure(
                get_disaster_network_viz, combined_disaster_data_data,
                title="Disaster types that strike together",
                subtitle="Edges connect types whose yearly impacts correlate",
                info="An edge means the two disaster types tend to have similar "
                     "impact years; thicker edges are stronger correlations.",
                span=6, height="460px",
            ),
            SafeFigure(
                get_multi_metric_parallel_viz, combined_disaster_data_data,
                title="All metrics, year by year",
                subtitle="Each line is one year traced across every impact metric",
                info="Follow a line to see how one year scored across all "
                     "metrics. Drag along an axis to filter years.",
                span=12, height="440px",
            ),
            SafeFigure(
                get_rolling_correlation_viz, combined_disaster_data_data,
                title="How the deaths–damages link changed",
                subtitle="5-year rolling correlation between deaths and damages",
                info="Above zero: deadly years were also costly years in that "
                     "window. The line moving toward zero means the link "
                     "weakened — often a sign of better protection.",
                span=12, height="400px",
            ),
            SafeFigure(
                get_scatter_matrix_viz, combined_disaster_data_data,
                title="Every metric against every other",
                subtitle="Scatter-plot matrix of impact metrics",
                info="Each panel plots one metric against another; diagonal "
                     "panels show each metric's own distribution.",
                span=12, height="700px",
            ),
        ]),
    ]


# --------------------------------------------------------------- tab 7 ------
def _stat_chip(value, label):
    return html.Div(className="stat-chip", children=[
        html.Strong(value), html.Span(label),
    ])


def _source_card(icon, title, provider, description, chips, fields, href=None,
                 link_label=None):
    return html.Section(className="card", style={"gridColumn": "span 6"},
                        children=[
        html.Header(className="card__header", children=[
            html.Div(className="card__heading card__heading--icon", children=[
                html.I(className=f"source-icon {icon}", **{"aria-hidden": "true"}),
                html.Div([
                    html.H3(title, className="card__title"),
                    html.P(provider, className="card__subtitle"),
                ]),
            ]),
        ]),
        html.Div(className="card__body card__body--pad", children=[
            html.P(description, className="source-desc"),
            html.Div(className="stat-chip-row", children=chips),
            html.P([html.Strong("Fields used: "), fields], className="source-fields"),
            html.A([link_label or "Visit source ", html.I(
                className="fa-solid fa-arrow-up-right-from-square",
                **{"aria-hidden": "true"})],
                href=href, target="_blank", rel="noopener",
                className="source-link") if href else None,
        ]),
    ])


def data_sources_tab():
    n_events = len(main_data)
    n_combined = len(combined_disaster_data_data)
    n_umap = len(umap_data)
    n_types = combined_disaster_data_data["Disaster Type"].nunique()
    return [
        ControlBar([], note="Every dataset behind the portal: what it contains, "
                            "where it comes from, and how it was processed."),
        html.Div(className="tab-grid", children=[
            _source_card(
                "fa-solid fa-house-flood-water",
                "Country-level disaster impacts", "Our World in Data · 1900–2024",
                "The core dataset: annual impacts per country for eight disaster "
                "types — deaths, injuries, people affected, people left homeless, "
                "assistance provided, and economic damages as a share of GDP. "
                "Powers the Overview, Disaster Type Analysis and "
                "Trends & Correlations tabs.",
                [_stat_chip(f"{n_combined:,}", "country-year rows"),
                 _stat_chip(str(n_types), "disaster types"),
                 _stat_chip("125", "years")],
                "Country name, Year, Disaster Type, Deaths, Injuries, Affected, "
                "Rendered homeless, Assistance, Damages (% GDP)",
                href="https://ourworldindata.org/natural-disasters",
                link_label="ourworldindata.org/natural-disasters ",
            ),
            _source_card(
                "fa-solid fa-triangle-exclamation",
                "Event-level disaster records", "EM-DAT schema · 2000–2024",
                "One row per recorded disaster event, with coordinates, "
                "magnitude, human losses and monetary damages — enriched with "
                "GDP per capita, HDI, hospital beds, urbanization and governance "
                "indicators. Powers the Country Risk Profiles tab and the "
                "event map.",
                [_stat_chip(f"{n_events:,}", "events"),
                 _stat_chip("60+", "columns"),
                 _stat_chip("25", "years")],
                "Disaster Type, Location, Latitude/Longitude, Start Year, Total "
                "Deaths, Total Affected, Total Damage, gdp_per_capita, hdi, "
                "gov_effectiveness, World Risk Index",
                href="https://www.emdat.be",
                link_label="emdat.be (CRED, UCLouvain) ",
            ),
            _source_card(
                "fa-solid fa-scale-unbalanced",
                "World Risk Index", "WorldRiskReport (IFHV) · 2000–2024",
                "Roughly 50 indicators per country-year covering exposure, "
                "vulnerability, susceptibility, coping capacity and adaptive "
                "capacity. This is the high-dimensional space the Risk Clusters "
                "tab reduces to 2-D with UMAP.",
                [_stat_chip(f"{n_umap:,}", "country-years"),
                 _stat_chip("~50", "indicators"),
                 _stat_chip("7", "K-Means clusters")],
                "W (risk), E (exposure), V (vulnerability), S, C, A plus their "
                "published sub-scores (EI_*, SI_*, CI_*, AI_*)",
                href="https://weltrisikobericht.de/en/",
                link_label="weltrisikobericht.de ",
            ),
            _source_card(
                "fa-solid fa-city",
                "World cities gazetteer", "countries-states-cities database",
                "151,855 cities with coordinates and country codes, used to "
                "geocode event locations for the disaster events map on the "
                "Country Risk Profiles tab.",
                [_stat_chip("151,855", "cities"),
                 _stat_chip("250", "countries & territories")],
                "name, country_code, latitude, longitude",
                href="https://github.com/dr5hn/countries-states-cities-database",
                link_label="github.com/dr5hn ",
            ),
            ChartCard(
                "Processing pipeline", span=12,
                subtitle="How raw files become the charts you see "
                         "(preprocessing/ and utils/data_loader.py)",
                children=html.Div(className="prose card__body--pad", children=[
                    html.Ol(className="pipeline-list", children=[
                        html.Li([html.Strong("Ingest & merge — "),
                                 "eight per-disaster CSVs are concatenated into "
                                 "one master table, each row tagged with its "
                                 "Disaster Type."]),
                        html.Li([html.Strong("Clean & standardize — "),
                                 "missing impact values are zero-imputed "
                                 "(absence of a record = no recorded impact); "
                                 "column names are unified."]),
                        html.Li([html.Strong("Geocode — "),
                                 "country names are converted to ISO 3166-1 "
                                 "alpha-3 codes with pycountry fuzzy lookup so "
                                 "they bind to map polygons."]),
                        html.Li([html.Strong("Pre-aggregate — "),
                                 "heavy transforms (tab3_*.csv, "
                                 "umap_embedding.csv) are computed once, "
                                 "offline, so the live dashboard only reads "
                                 "ready-made tables."]),
                        html.Li([html.Strong("Reduce & cluster — "),
                                 "preprocessing/compute_umap.py standardizes "
                                 "the ~50 risk indicators and projects them to "
                                 "2-D with UMAP (n_neighbors 15, min_dist 0.1, "
                                 "seed 42), joining K-Means cluster labels."]),
                    ]),
                    html.P("All processed artifacts live in data/processed/ — "
                           "delete one and its preprocessing script can "
                           "regenerate it.", className="source-fields"),
                ]),
            ),
        ]),
    ]


# ------------------------------------------------------------ assembling ----
def region_widgets(region):
    builders = {
        "overview": overview_tab,
        "disaster-analysis": disaster_analysis_tab,
        "economic-impact": economic_impact_tab,
        "country-profiles": country_profiles_tab,
        "risk-clusters": risk_clusters_tab,
        "trends-correlations": trends_correlations_tab,
        "data-sources": data_sources_tab,
    }
    builder = builders.get(region)
    if builder is None:
        return [ErrorCard("Unknown tab.")]
    try:
        return builder()
    except Exception as e:
        return [ErrorCard(f"This tab failed to build — {type(e).__name__}: {e}")]


def ContentSection(region):
    return html.Div(
        id=f"content-{region}",
        className="content-section active" if region == "overview" else "content-section",
        children=region_widgets(region),
    )
