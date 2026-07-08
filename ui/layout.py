# layout.py
from dash import html

from .components import Topbar, Sidebar, ContentSection, tabs

layout = html.Div(id="app-container", className="layout dark", children=[
    Topbar,
    Sidebar,
    html.Main(id="main-content", className="main-content", children=[
        ContentSection(key) for key, _, _ in tabs
    ]),
])
