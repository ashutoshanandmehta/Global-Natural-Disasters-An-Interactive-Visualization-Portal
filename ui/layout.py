# layout.py
from dash import html
from ui.components import Topbar, Sidebar, ContentSection

tabs = ["overview","disaster-analysis", "economic-impact", "country-profiles", "trends-correlations"]

layout = html.Div(id="app-container", className="layout dark", children=[
    Topbar,
    Sidebar,
    html.Div(id="main-content", className="main-content main-content--grid", children=[
        ContentSection(tab) for tab in tabs
    ])
])
