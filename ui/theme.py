# theme.py
# Design system for the portal: color tokens, a Plotly figure themer, and the
# reusable card/control components every tab is built from.
#
# Palette: validated dark-surface categorical set (CVD-checked); one hue per
# disaster type, fixed everywhere so a color always means the same hazard.

from dash import html, dcc

# ---------------------------------------------------------------- tokens ----
PAGE_BG = "#0d0d0d"
CARD_BG = "#1a1a19"
HAIRLINE = "#2c2c2a"
INK = "#ffffff"
INK_2 = "#c3c2b7"
INK_MUTED = "#898781"
ACCENT = "#3987e5"

# Fixed hue per disaster type — never reassigned when filters change.
DISASTER_COLORS = {
    "Flood": "#3987e5",                 # blue — water
    "Storms": "#199e70",                # aqua — wind/water
    "Storm": "#199e70",
    "Droughts": "#c98500",              # yellow — arid
    "Drought": "#c98500",
    "Mass_Movements_Dry": "#008300",    # green — land
    "Mass movement (dry)": "#008300",
    "Extreme_Temperatures": "#e66767",  # red — heat
    "Extreme temperature": "#e66767",
    "Wildfires": "#d95926",             # orange — fire
    "Wildfire": "#d95926",
    "Volcanoes": "#9085e9",             # violet
    "Volcanic activity": "#9085e9",
    "Earthquakes": "#d55181",           # magenta
    "Earthquake": "#d55181",
}
DISASTER_COLOR_SEQ = ["#3987e5", "#199e70", "#c98500", "#008300",
                      "#9085e9", "#e66767", "#d55181", "#d95926"]

# Cluster hues for the UMAP tab (7 clusters; -1 = unclustered → muted).
CLUSTER_COLORS = {
    0: "#3987e5", 1: "#199e70", 2: "#c98500", 3: "#9085e9",
    4: "#e66767", 5: "#d55181", 6: "#d95926", -1: "#898781",
}

SEQUENTIAL_SCALE = [
    [0.0, "#cde2fb"], [0.25, "#86b6ef"], [0.5, "#3987e5"],
    [0.75, "#1c5cab"], [1.0, "#0d366b"],
]

FONT_STACK = 'system-ui, -apple-system, "Segoe UI", sans-serif'


# ------------------------------------------------------------ fig themer ----
def apply_theme(fig, height=None):
    """Restyle any Plotly figure to the portal's dark design system."""
    if fig is None or isinstance(fig, dict):
        return fig
    layout_kwargs = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_STACK, size=12, color=INK_2),
        title_font=dict(size=13, color=INK),
        margin=dict(l=48, r=24, t=48, b=40),
        hoverlabel=dict(
            bgcolor="#242423", bordercolor=HAIRLINE,
            font=dict(family=FONT_STACK, size=12, color=INK),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color=INK_2),
        ),
    )
    if height:
        layout_kwargs["height"] = height
    fig.update_layout(**layout_kwargs)
    fig.update_xaxes(gridcolor=HAIRLINE, zerolinecolor=HAIRLINE,
                     linecolor=HAIRLINE, tickfont=dict(color=INK_MUTED))
    fig.update_yaxes(gridcolor=HAIRLINE, zerolinecolor=HAIRLINE,
                     linecolor=HAIRLINE, tickfont=dict(color=INK_MUTED))
    try:
        fig.update_geos(bgcolor="rgba(0,0,0,0)", framecolor=HAIRLINE,
                        coastlinecolor="#4a4a47", landcolor="#242423",
                        oceancolor="#151514", showocean=True,
                        lakecolor="#151514")
    except Exception:
        pass
    try:
        fig.update_polars(
            bgcolor="rgba(0,0,0,0)",
            angularaxis=dict(gridcolor=HAIRLINE, linecolor=HAIRLINE,
                             tickfont=dict(color=INK_2)),
            radialaxis=dict(gridcolor=HAIRLINE, linecolor=HAIRLINE,
                            tickfont=dict(color=INK_MUTED)),
        )
    except Exception:
        pass
    return fig


# ------------------------------------------------------------ components ----
def InfoTip(text):
    """Small ⓘ marker with a hover explanation (help & documentation)."""
    return html.Span(
        className="info-tip", tabIndex=0, children=[
            "?",
            html.Span(text, className="info-tip__bubble", role="tooltip"),
        ],
    )


def ChartCard(title, children, info=None, subtitle=None, span=12, min_height=None,
              controls=None):
    """Uniform chart container: header (title · subtitle · info) + body."""
    header_right = []
    # NB: `is not None`, not truthiness — a childless Dash component has len() 0
    if controls is not None:
        header_right.append(html.Div(controls, className="card__controls"))
    if info:
        header_right.append(InfoTip(info))
    style = {"gridColumn": f"span {span}"}
    if min_height:
        style["minHeight"] = min_height
    return html.Section(className="card", style=style, children=[
        html.Header(className="card__header", children=[
            html.Div(className="card__heading", children=[
                html.H3(title, className="card__title"),
                html.P(subtitle, className="card__subtitle") if subtitle else None,
            ]),
            html.Div(className="card__header-right", children=header_right),
        ]),
        html.Div(className="card__body", children=children),
    ])


def LoadedGraph(graph_id, height="420px", figure=None):
    """dcc.Graph wrapped in a loading spinner (visibility of system status)."""
    graph_kwargs = dict(
        id=graph_id,
        config={"displayModeBar": False, "responsive": True},
        style={"height": height, "width": "100%"},
    )
    if figure is not None:
        graph_kwargs["figure"] = figure
    return dcc.Loading(
        type="circle", color=ACCENT, delay_show=250,
        children=dcc.Graph(**graph_kwargs),
    )


def ErrorCard(message, style=None, span=None):
    """Visible failure state instead of a fake skeleton (error recognition)."""
    s = dict(style or {})
    if span:
        s["gridColumn"] = f"span {span}"
    return html.Section(className="card card--error", style=s, children=[
        html.Div(className="error-state", children=[
            html.Span("!", className="error-state__badge"),
            html.Div([
                html.P("This chart couldn't be drawn.", className="error-state__title"),
                html.P(message, className="error-state__detail"),
            ]),
        ]),
    ])


def SafeFigure(viz_func, data, *, title, info=None, subtitle=None, span=12,
               height="420px", **kwargs):
    """Build a themed, static figure card; on failure, show a real error card."""
    try:
        fig = viz_func(data, **kwargs)
        if fig is None:
            raise ValueError("the chart function returned no figure")
        apply_theme(fig)
        return ChartCard(
            title, info=info, subtitle=subtitle, span=span,
            children=dcc.Graph(
                figure=fig, config={"displayModeBar": False, "responsive": True},
                style={"height": height, "width": "100%"},
            ),
        )
    except Exception as e:
        return ErrorCard(f"{type(e).__name__}: {e}", span=span)


def KpiTile(tile_id, label, hint=None):
    return html.Div(className="kpi", children=[
        html.Span(label, className="kpi__label"),
        html.Strong("—", id=tile_id, className="kpi__value"),
        html.Span(hint or "", className="kpi__hint"),
    ])


def ControlBar(children, note=None):
    """One consistent filter row per tab (recognition over recall)."""
    items = list(children)
    if note:
        items.append(html.Span(note, className="control-bar__note"))
    return html.Div(className="control-bar", children=items)


def Field(label, control):
    return html.Div(className="field", children=[
        html.Label(label, className="field__label"),
        control,
    ])
