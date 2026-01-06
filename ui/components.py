# components.py
from dash import html
from .widgets import SafeVizWidget, data_choropleth, data_gdp, data_bar, data_pie, data_treemap, data_sankey
from visualizations.viz1 import get_sunburst_viz
from visualizations.tab2_sankey import get_sankey_viz
from visualizations.tab2_bar_chart import get_bar_viz
from visualizations.tab1_treemap import get_treemap_viz
from visualizations.tab2_pie_chart import get_pie_viz
from visualizations.tab1_chloropleth import get_choropleth_viz

# Topbar
Topbar = html.Div(className="topbar", children=[
    html.Div("My Dashboard", className="topbar-logo"),
    html.Div(className="theme-toggle theme-toggle--dark", id="theme-toggle", children=[
        html.Div(className="theme-toggle__ball")
    ])
])

# Sidebar tabs
tabs = [
    ("overview", "🌍", "Overview & Global Patterns"),
    ("disaster-analysis", "⚡", "Disaster Type Analysis"),
    ("economic-impact", "💰", "Economic Impact & Vulnerability"),
    ("country-profiles", "📊", "Country Risk Profiles"),
    ("trends-correlations", "📈", "Trends & Correlations")
]

SidebarTabs = html.Div(className="sidebar-tabs", children=[
    html.Div(className=f"sidebar-tab {'sidebar-tab--active' if region[0]=='overview' else ''}", 
             **{"data-tab": region[0]}, children=[
        html.Div(region[1], className="icon"),
        html.Span(region[2], className="tab-label")
    ]) for region in tabs
])

# Sidebar
Sidebar = html.Div(id="sidebar", className="sidebar", children=[
    html.Button(id="sidebar-toggle", className="sidebar-toggle", children=[
        html.Span(className="bar"),
        html.Span(className="bar"),
        html.Span(className="bar")
    ]),
    SidebarTabs
])

# Skeleton widget
def SkeletonWidget(style=None):
    return html.Div(
        className="widget widget--skeleton",
        style=style or {},
        children=[
            html.Div(className="skeleton-bar"),
            html.Div(className="skeleton-bar short"),
            html.Div(className="skeleton-circle")
        ]
    )

# Per-region widget layout

def region_widgets(region):
    if region == "overview":
        return [
            SafeVizWidget(get_choropleth_viz, data_choropleth, {"gridColumn": "1 / 4", "gridRow": "3 / 6"}),
            SafeVizWidget(get_sunburst_viz, data_gdp, {"gridColumn": "1 / 2", "gridRow": "1 / 2"}),
            SafeVizWidget(get_bar_viz, data_bar, {"gridColumn": "2 / 4", "gridRow": "1 / 2"}),
            SafeVizWidget(get_pie_viz, data_pie, {"gridColumn": "1 / 2", "gridRow": "2 / 3"}),
            SafeVizWidget(get_treemap_viz, data_treemap, {"gridColumn": "2 / 3", "gridRow": "2 / 3"}),
            SafeVizWidget(get_sankey_viz, data_sankey, {"gridColumn": "3 / 4", "gridRow": "2 / 3"}),
        ]
    elif region == "disaster-analysis":
        return [
            SkeletonWidget({"gridColumn": "1 / 4", "gridRow": "1 / 2", "background": "#b33"}),
            SkeletonWidget({"gridColumn": "1 / 2", "gridRow": "2 / 3"}),
            SkeletonWidget({"gridColumn": "2 / 3", "gridRow": "2 / 3"}),
            SkeletonWidget({"gridColumn": "3 / 4", "gridRow": "2 / 3"}),
            SkeletonWidget({"gridColumn": "1 / 2", "gridRow": "3 / 4"}),
            SkeletonWidget({"gridColumn": "2 / 3", "gridRow": "3 / 4"}),
            SkeletonWidget({"gridColumn": "3 / 4", "gridRow": "3 / 4", "background": "#b33"})
        ]
    elif region == "economic-impact":
        return [
            SkeletonWidget({"gridColumn": "1 / 4", "gridRow": "1 / 2"}),
            SkeletonWidget({"gridColumn": "1 / 4", "gridRow": "2 / 3", "background": "#b33"}),
            SkeletonWidget({"gridColumn": "1 / 2", "gridRow": "3 / 4"}),
            SkeletonWidget({"gridColumn": "2 / 3", "gridRow": "3 / 4"}),
            SkeletonWidget({"gridColumn": "3 / 4", "gridRow": "3 / 4"}),
            SkeletonWidget({"gridColumn": "2 / 4", "gridRow": "2 / 3"})
        ]
    elif region == "country-profiles":
        return [
            SkeletonWidget({"gridColumn": "1 / 4", "gridRow": "1 / 2", "background": "#b33"}),
            SkeletonWidget({"gridColumn": "1 / 2", "gridRow": "2 / 3"}),
            SkeletonWidget({"gridColumn": "2 / 3", "gridRow": "2 / 3"}),
            SkeletonWidget({"gridColumn": "3 / 4", "gridRow": "2 / 3"}),
            SkeletonWidget({"gridColumn": "1 / 2", "gridRow": "3 / 4"}),
            SkeletonWidget({"gridColumn": "2 / 4", "gridRow": "3 / 4"})
        ]
    elif region == "trends-correlations":
        return [
            SkeletonWidget({"gridColumn": "1 / 4", "gridRow": "1 / 2"}),
            SkeletonWidget({"gridColumn": "2 / 3", "gridRow": "2 / 3"}),
            SkeletonWidget({"gridColumn": "3 / 4", "gridRow": "2 / 3"}),
            SkeletonWidget({"gridColumn": "1 / 2", "gridRow": "2 / 3"}),
            SkeletonWidget({"gridColumn": "1 / 3", "gridRow": "3 / 4"}),
            SkeletonWidget({"gridColumn": "3 / 4", "gridRow": "3 / 4"})
        ]
    else:
        return [SkeletonWidget()]

def ContentSection(region):
    return html.Div(
        id=f"content-{region}",
        className="content-section active" if region == "overview" else "content-section",
        children=region_widgets(region)
    )
