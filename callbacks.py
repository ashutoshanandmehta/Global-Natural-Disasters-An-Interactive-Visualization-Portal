# callbacks.py
from dash import Input, Output, callback, html, dcc, State, callback_context
import pandas as pd
from pathlib import Path
from utils.data_loader import load_all_csvs
from visualizations.tab4_small_plots import plot_disaster_types_by_year
from visualizations.tab4_small_plots import plot_disaster_types_pie_chart
from ui.theme import apply_theme

# Column names containing apostrophes (kept out of f-strings for Python < 3.12)
COL_DAMAGE = "Total Damage ('000 US$)"
COL_RECON = "Reconstruction Costs ('000 US$)"
COL_INSURED = "Insured Damage ('000 US$)"
COL_AID = "AID Contribution ('000 US$)"

# Load data - specifically use final_risk_merged.csv, ranked_data.csv, and cities.csv
data_dir = Path(__file__).resolve().parent / "data" / "Risk_Analysis"
risk_data_path = data_dir / "final_risk_merged.csv"
ranked_data_path = data_dir / "ranked_data.csv"
cities_data_path = data_dir / "cities.csv"
cluster_data_path = data_dir / "risk_data_clustered.csv"
index_data_path = data_dir / "index.csv"

# Load the risk data
try:
    index_data = pd.read_csv(index_data_path)
    risk_data = pd.read_csv(risk_data_path)
    cluster_data = pd.read_csv(cluster_data_path)
    print(f"Loaded risk data with {len(risk_data)} rows and columns: {list(risk_data.columns)}")
except Exception as e:
    print(f"Error loading risk data: {e}")
    risk_data = None

# Load the ranked data
try:
    ranked_data = pd.read_csv(ranked_data_path)
    print(f"Loaded ranked data with {len(ranked_data)} rows and columns: {list(ranked_data.columns)}")
except Exception as e:
    print(f"Error loading ranked data: {e}")
    ranked_data = None

# Load the cities data
try:
    cities_data = pd.read_csv(cities_data_path)
    print(f"Loaded cities data with {len(cities_data)} rows and columns: {list(cities_data.columns)}")
except Exception as e:
    print(f"Error loading cities data: {e}")
    cities_data = None

# Also load processed data as fallback
processed_data_dir = Path(__file__).resolve().parent / "data" / "processed"
data_vars = load_all_csvs(processed_data_dir)

# Get the main disaster data as fallback
if 'combined_disaster_data_data' in data_vars:
    disaster_data = data_vars['combined_disaster_data_data']
else:
    # Fallback: try to find any CSV with country data
    disaster_data = None
    for var_name, df in data_vars.items():
        if 'Country' in df.columns and 'Year' in df.columns:
            disaster_data = df
            break

@callback(
    Output("country-selector", "options"),
    Input("country-selector", "id")
)
def populate_country_dropdown(trigger):
    """Populate the country dropdown with available countries from the risk dataset."""
    if risk_data is None:
        return []
    
    # Get unique countries from the risk dataset
    if 'Country_x' in risk_data.columns:
        countries = sorted(risk_data['Country_x'].dropna().unique())
    else:
        return []
    
    # Create options for dropdown
    options = [{"label": country, "value": country} for country in countries]
    return options

@callback(
    Output("year-selector", "options"),
    Input("country-selector", "value"),
    Input("year-selector", "id")
)
def populate_year_dropdown(selected_country, trigger):
    """Populate the year dropdown based on selected country from risk dataset, always including an 'All' option."""
    if risk_data is None or not selected_country:
        return [{"label": "All", "value": "all"}]
    if 'Country_x' in risk_data.columns:
        country_data = risk_data[risk_data['Country_x'] == selected_country]
    else:
        return [{"label": "All", "value": "all"}]
    if 'Start Year' in country_data.columns:
        years = sorted(country_data['Start Year'].dropna().unique())
    else:
        return [{"label": "All", "value": "all"}]
    options = [{"label": "All", "value": "all"}] + [
        {"label": str(int(year)), "value": int(year)} for year in years if pd.notna(year)
    ]
    return options

@callback(
    Output("year-selector", "value"),
    Input("year-selector", "options")
)
def set_default_year(year_options):
    """Set the first available year as default when year options change."""
    if year_options and len(year_options) > 0:
        return year_options[0]["value"]
    return None

@callback(
    Output("click-state", "data"),
    Output("region-hotspot-map", "clickData"),
    Input("region-hotspot-map", "clickData"),
    Input("reset-metrics-btn", "n_clicks"),
    Input("country-selector", "value"),
    Input("year-selector", "value"),
    prevent_initial_call=True
)
def update_click_state(clickData, reset_clicks, selected_country, selected_year):
    """Update the click state based on map clicks, reset button, country, and year changes."""
    ctx = callback_context
    if not ctx.triggered:
        return {"show_disaster": False}, None
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Reset to country view for any of these triggers
    if trigger_id in ["reset-metrics-btn", "country-selector", "year-selector"]:
        return {"show_disaster": False}, None  # Clear click data and show country summary
    
    elif trigger_id == "region-hotspot-map":
        if clickData and clickData.get("points") and len(clickData["points"]) > 0:
            return {"show_disaster": True}, clickData
        else:
            return {"show_disaster": False}, None
    
    return {"show_disaster": False}, None

@callback(
    Output("country-selector", "value"),
    Input("country-selector", "options")
)
def set_default_country(country_options):
    """Set the first available country as default when country options change."""
    if country_options and len(country_options) > 0:
        return country_options[0]["value"]
    return None

# Metrics card callback
@callback(
    Output("metrics-card", "children"),
    Input("region-hotspot-map", "clickData"),
    Input("country-selector", "value"),
    Input("year-selector", "value"),
    State("click-state", "data"),
)
def update_metrics_card(clickData, selected_country, selected_year, click_state):
    if risk_data is None:
        return []
    
    # Check if we should show disaster details based on click state
    show_disaster_details = click_state.get("show_disaster", False) if click_state else False
    
    # If a map point is clicked, show disaster info
    if show_disaster_details and clickData and clickData.get("points") and len(clickData["points"]) > 0:
        point = clickData["points"][0]
        disaster_id = None
        if "customdata" in point and point["customdata"]:
            # Extract the disaster ID from the customdata
            disaster_id = point["customdata"][0] if isinstance(point["customdata"], list) else point["customdata"]
        elif "text" in point and point["text"]:
            lat = point.get("lat")
            lon = point.get("lon")
            # Handle "all" years case
            if selected_year == "all":
                filtered = risk_data[risk_data["Country_x"] == selected_country]
            else:
                filtered = risk_data[(risk_data["Country_x"] == selected_country) & (risk_data["Start Year"] == selected_year)]
            if lat is not None and lon is not None and isinstance(filtered, pd.DataFrame) and not filtered.empty:
                match = filtered[(filtered["Latitude"] == lat) & (filtered["Longitude"] == lon)]
                if isinstance(match, pd.DataFrame) and not match.empty:
                    disaster_id = match.iloc[0]["DisNo."]
        if disaster_id is not None:
            row = risk_data[risk_data["DisNo."] == disaster_id]
            if isinstance(row, pd.DataFrame) and not row.empty:
                row = row.iloc[0]
                summary = [
                    html.Div(
                        className="metrics-card-header",
                        style={"borderBottom": "1px solid rgba(255,255,255,0.1)", "paddingBottom": "8px", "marginBottom": "12px"},
                        children=[
                            html.H3(f"{row['Disaster Type']} in {row['Country_x']} ({row['Start Year']})", style={"color": "white", "margin": "0", "fontSize": "14px", "fontWeight": "600"}),
                            html.P(row['Location'] if pd.notna(row['Location']) else "", style={"color": "#ccc", "margin": "2px 0 0 0", "fontSize": "10px"})
                        ]
                    ),
                    html.Div([
                        # Basic Information
                        html.Div([
                            html.Div(["🆔", html.Span(f" {row['DisNo.']}" if 'DisNo.' in row else "")], style={"fontSize": "12px", "marginBottom": "4px"}),
                            html.Div(["Type: ", html.B(row['Disaster Type'] if 'Disaster Type' in row else "")], style={"fontSize": "12px", "marginBottom": "4px"}),
                            html.Div(["Subgroup: ", html.B(row['Disaster Subgroup'] if 'Disaster Subgroup' in row and pd.notna(row['Disaster Subgroup']) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                            html.Div(["Subtype: ", html.B(row['Disaster Subtype'] if 'Disaster Subtype' in row and pd.notna(row['Disaster Subtype']) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                        ], style={"marginBottom": "12px", "paddingBottom": "8px", "borderBottom": "1px solid rgba(255,255,255,0.1)"}),
                        
                        # Event Details
                        html.Div([
                            html.Div(["📅 Start: ", html.B(f"{row['Start Day']}/{row['Start Month']}/{row['Start Year']}" if all(pd.notna(row.get(col, None)) for col in ['Start Day', 'Start Month', 'Start Year']) else f"{row['Start Year']}" if pd.notna(row.get('Start Year', None)) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                            html.Div(["📅 End: ", html.B(f"{row['End Day']}/{row['End Month']}/{row['End Year']}" if all(pd.notna(row.get(col, None)) for col in ['End Day', 'End Month', 'End Year']) else f"{row['End Year']}" if pd.notna(row.get('End Year', None)) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                            html.Div(["📋 Event: ", html.B(row['Event Name'] if 'Event Name' in row and pd.notna(row['Event Name']) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                            html.Div(["📍 Origin: ", html.B(row['Origin'] if 'Origin' in row and pd.notna(row['Origin']) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                        ], style={"marginBottom": "12px", "paddingBottom": "8px", "borderBottom": "1px solid rgba(255,255,255,0.1)"}),
                        
                        # Impact Metrics
                        html.Div([
                            html.Div(["💀 Deaths: ", html.B(f"{int(row['Total Deaths']):,}" if 'Total Deaths' in row and pd.notna(row['Total Deaths']) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                            html.Div(["🏥 Injured: ", html.B(f"{int(row['No. Injured']):,}" if 'No. Injured' in row and pd.notna(row['No. Injured']) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                            html.Div(["👥 Affected: ", html.B(f"{int(row['Total Affected']):,}" if 'Total Affected' in row and pd.notna(row['Total Affected']) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                            html.Div(["🏠 Homeless: ", html.B(f"{int(row['No. Homeless']):,}" if 'No. Homeless' in row and pd.notna(row['No. Homeless']) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                        ], style={"marginBottom": "12px", "paddingBottom": "8px", "borderBottom": "1px solid rgba(255,255,255,0.1)"}),
                        
                        # Economic Impact
                        html.Div([
                            html.Div(["💰 Total Damage: ", html.B(f"${int(row[COL_DAMAGE]):,}" if COL_DAMAGE in row and pd.notna(row[COL_DAMAGE]) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                            html.Div(["🏗️ Reconstruction: ", html.B(f"${int(row[COL_RECON]):,}" if COL_RECON in row and pd.notna(row[COL_RECON]) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                            html.Div(["🛡️ Insured Damage: ", html.B(f"${int(row[COL_INSURED]):,}" if COL_INSURED in row and pd.notna(row[COL_INSURED]) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                            html.Div(["🤝 AID Contribution: ", html.B(f"${int(row[COL_AID]):,}" if COL_AID in row and pd.notna(row[COL_AID]) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                        ], style={"marginBottom": "12px", "paddingBottom": "8px", "borderBottom": "1px solid rgba(255,255,255,0.1)"}),
                        
                        # Technical Details
                        html.Div([
                            html.Div(["🌊 Magnitude: ", html.B(f"{row['Magnitude']} {row['Magnitude Scale']}" if 'Magnitude' in row and pd.notna(row['Magnitude']) and 'Magnitude Scale' in row and pd.notna(row['Magnitude Scale']) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                            html.Div(["🏛️ Declaration: ", html.B(row['Declaration'] if 'Declaration' in row and pd.notna(row['Declaration']) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                            html.Div(["📢 Appeal: ", html.B(row['Appeal'] if 'Appeal' in row and pd.notna(row['Appeal']) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                            # html.Div(["🏢 Admin Units: ", html.B(row['Admin Units'] if 'Admin Units' in row and pd.notna(row['Admin Units']) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                        ], style={"marginBottom": "12px", "paddingBottom": "8px", "borderBottom": "1px solid rgba(255,255,255,0.1)"}),
                        
                        # Risk Metrics
                        html.Div([
                            html.Div(["🌍 World Risk Index: ", html.B(f"{row['World Risk Index']:.2f}" if 'World Risk Index' in row and pd.notna(row['World Risk Index']) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                            html.Div(["⚠️ Disaster Score: ", html.B(f"{row['Disaster_Score']:.2f}" if 'Disaster_Score' in row and pd.notna(row['Disaster_Score']) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                            html.Div(["📊 Average Risk Index: ", html.B(f"{row['Average_Risk_Index']:.2f}" if 'Average_Risk_Index' in row and pd.notna(row['Average_Risk_Index']) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                            html.Div(["🎯 Vulnerability: ", html.B(f"{row['Vulnerability']:.2f}" if 'Vulnerability' in row and pd.notna(row['Vulnerability']) else "N/A")], style={"fontSize": "12px", "marginBottom": "4px"}),
                        ], style={"marginBottom": "8px"}),
                    ], style={"marginTop": "8px"})
                ]
                return summary
    # Otherwise, show default metrics (for all years if year is 'all')
    if not selected_country or risk_data is None:
        return [
            html.Div(
                className="metrics-card-empty",
                children=[
                    html.H3("No Data Available", style={"color": "#ff6b6b", "margin": "0"}),
                    html.P(f"No data found for {selected_country}", style={"color": "#ccc", "margin": "5px 0 0 0"})
                ]
            )
        ]
    
    try:
        if selected_year == "all":
            # Show metrics for all years for the selected country
            country_year_data = risk_data[risk_data['Country_x'] == selected_country]
            bar_fig = apply_theme(plot_disaster_types_pie_chart(risk_data, selected_country, None))  # Pass None for year to show all years
        else:
            country_year_data = risk_data[(risk_data['Country_x'] == selected_country) & (risk_data['Start Year'] == selected_year)]
            bar_fig = apply_theme(plot_disaster_types_pie_chart(risk_data, selected_country, selected_year))
        
        if country_year_data.empty:
            return [
                html.Div(
                    className="metrics-card-empty",
                    children=[
                        html.H3("No Data Available", style={"color": "#ff6b6b", "margin": "0"}),
                        html.P(f"No data found for {selected_country}", 
                               style={"color": "#ccc", "margin": "5px 0 0 0"})
                    ]
                )
            ]
        
        # Get ranking data for the selected country and year
        ranking_info = {}
        if ranked_data is not None:
            if selected_year == "all":
                # For "all" years, get the most recent year's ranking data
                country_rank_data = ranked_data[ranked_data['Country_x'] == selected_country]
                if not country_rank_data.empty:
                    # Get the most recent year
                    latest_year = country_rank_data['Start Year'].max()
                    country_rank_data = country_rank_data[country_rank_data['Start Year'] == latest_year]
            else:
                country_rank_data = ranked_data[
                    (ranked_data['Country_x'] == selected_country) & 
                    (ranked_data['Start Year'] == selected_year)
                ]
            
            if not country_rank_data.empty:
                # Get ranking columns
                rank_columns = ['rank_damages', 'rank_risk_y', 'rank_gdp', 'rank_hdi_y', 'rank_vulnerability']
                for col in rank_columns:
                    if col in country_rank_data.columns:
                        ranking_info[col] = country_rank_data[col].iloc[0]
        
        # Calculate metrics
        metrics = {}
        
        # World Risk Index (average if multiple records)
        if 'World Risk Index' in country_year_data.columns:
            metrics['World Risk Index'] = country_year_data['World Risk Index'].mean()
        
        # Total Deaths
        if 'Total Deaths' in country_year_data.columns:
            metrics['Total Deaths'] = country_year_data['Total Deaths'].sum()
        
        # Total Damage (in thousands of US$)
        if 'Total Damage (\'000 US$)' in country_year_data.columns:
            metrics['Total Damage'] = country_year_data['Total Damage (\'000 US$)'].sum()
        
        # Total Affected
        if 'Total Affected' in country_year_data.columns:
            metrics['Total Affected'] = country_year_data['Total Affected'].sum()
        
        # Number of Disasters
        metrics['Number of Disasters'] = len(country_year_data)
        
        # Average Risk Index
        if 'Average_Risk_Index' in country_year_data.columns:
            metrics['Average Risk Index'] = country_year_data['Average_Risk_Index'].mean()
        
        # Create compact metric cards
        metric_cards = []
        
        # Define metric display info with rankings
        metric_info = {
            'World Risk Index': {'icon': '🌍', 'color': '#ff6b6b', 'format': '.2f', 'rank_key': 'rank_risk_y'},
            'Total Deaths': {'icon': '💀', 'color': '#ff8e8e', 'format': ',.0f'},
            'Total Damage': {'icon': '💰', 'color': '#ffd93d', 'format': ',.0f', 'rank_key': 'rank_damages'},
            'Total Affected': {'icon': '👥', 'color': '#6bcf7f', 'format': ',.0f'},
            'Number of Disasters': {'icon': '⚡', 'color': '#4dabf7', 'format': ',.0f'},
            
        }
        
        # Add ranking metrics
        for rank_key, rank_value in ranking_info.items():
            if pd.notna(rank_value):
                for metric_name, info in metric_info.items():
                    if info.get('rank_key') == rank_key:
                        metrics[metric_name] = rank_value
                        break
        
        for metric_name, value in metrics.items():
            if pd.notna(value) and value != 0:
                info = metric_info.get(metric_name, {'icon': '📈', 'color': '#868e96', 'format': ',.0f'})
                
                # Format the value
                if info['format'].startswith(','):
                    formatted_value = f"{value:{info['format']}}"
                else:
                    formatted_value = f"{value:{info['format']}}"
                
                # Add units for damage
                if metric_name == 'Total Damage':
                    formatted_value += " (000 US$)"
                
                # Add rank indicator for ranking metrics
                rank_indicator = ""
                if 'Rank' in metric_name:
                    rank_indicator = f" (Rank #{int(value)})"
                    formatted_value = f"#{int(value)}"
                
                metric_cards.append(
                    html.Div(
                        className="metric-item-compact",
                        style={
                            "background": f"linear-gradient(135deg, {info['color']}20, {info['color']}10)",
                            "border": f"1px solid {info['color']}40",
                            "borderRadius": "8px",
                            "padding": "8px 12px",
                            "margin": "4px 0",
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "8px",
                            "fontSize": "12px"
                        },
                        children=[
                            html.Div(
                                style={
                                    "fontSize": "16px",
                                    "width": "24px",
                                    "textAlign": "center"
                                },
                                children=info['icon']
                            ),
                            html.Div(
                                style={"flex": "1", "minWidth": "0"},
                                children=[
                                    html.Div(
                                        metric_name,
                                        style={
                                            "fontSize": "10px",
                                            "color": "#ccc",
                                            "fontWeight": "500",
                                            "textTransform": "uppercase",
                                            "letterSpacing": "0.3px",
                                            "lineHeight": "1"
                                        }
                                    ),
                                    html.Div(
                                        formatted_value + rank_indicator,
                                        style={
                                            "fontSize": "14px",
                                            "fontWeight": "bold",
                                            "color": "white",
                                            "marginTop": "2px",
                                            "lineHeight": "1"
                                        }
                                    )
                                ]
                            )
                        ]
                    )
                )
        
        # Add the bar graph below the metrics
        metric_cards.append(
            html.Div(
                style={"marginTop": "16px"},
                children=[
                    dcc.Graph(
                        figure=bar_fig,
                        config={"displayModeBar": False},
                        style={"height": "220px"}
                    )
                ]
            )
        )
        return [
            html.Div(
                className="metrics-card-header",
                style={
                    "borderBottom": "1px solid rgba(255,255,255,0.1)",
                    "paddingBottom": "8px",
                    "marginBottom": "12px"
                },
                children=[
                    html.H3(
                        f"{selected_country} - {selected_year}",
                        style={
                            "color": "white",
                            "margin": "0",
                            "fontSize": "14px",
                            "fontWeight": "600"
                        }
                    ),
                    html.P(
                        "Key Metrics & Rankings",
                        style={
                            "color": "#ccc",
                            "margin": "2px 0 0 0",
                            "fontSize": "10px",
                            "textTransform": "uppercase",
                            "letterSpacing": "0.3px"
                        }
                    )
                ]
            )
        ] + metric_cards
        
    except Exception as e:
        print(f"Error updating metrics card: {e}")
        return [
            html.Div(
                className="metrics-card-error",
                children=[
                    html.H3("Error Loading Data", style={"color": "#ff6b6b", "margin": "0", "fontSize": "14px"}),
                    html.P(f"Could not load metrics for {selected_country}", 
                           style={"color": "#ccc", "margin": "5px 0 0 0", "fontSize": "12px"})
                ]
            )
        ]

# Initialize visualizations with default data
@callback(
    Output("country-risk-radar", "figure"),
    Input("country-selector", "options")
)
def initialize_risk_radar(country_options):
    """Initialize the risk radar chart with default data."""
    if not country_options or len(country_options) == 0:
        return {}
    
    default_country = country_options[0]["value"]
    try:
        from visualizations.tab4_risk_spider import country_risk_radar_yearly
        fig = country_risk_radar_yearly(risk_data, default_country)
        return apply_theme(fig)
    except Exception as e:
        print(f"Error initializing risk radar: {e}")
        return {}

    
    default_country = country_options[0]["value"]
    default_year = year_options[0]["value"]
    try:
        from visualizations.tab2_pie_chart import get_pie_viz
        fig = get_pie_viz(risk_data, default_country, "Total Deaths", default_year-5, default_year)
        return fig
    except Exception as e:
        print(f"Error initializing disaster pie chart: {e}")
        return {}


    
    default_country = country_options[0]["value"]
    try:
        from visualizations.tab2_radar_chart import get_radar_viz
        fig = get_radar_viz(risk_data, default_country, 2010, 2020)
        return fig
    except Exception as e:
        print(f"Error initializing vulnerability radar: {e}")
        return {}

# Callbacks to update visualizations based on selector changes
@callback(
    Output("country-risk-radar", "figure", allow_duplicate=True),
    Input("country-selector", "value"),
    # Input("analysis-type-selector", "value"),
    State("multi-country-selector", "value"),
    prevent_initial_call=True
)
def update_risk_radar(selected_country, selected_countries):
    """Update the risk radar chart based on selected country and analysis type, only if no multi-country selection."""
    if (selected_countries and len(selected_countries) > 0) or not selected_country:
        return {}
    try:
        from visualizations.tab4_risk_spider import country_risk_radar_yearly
        fig = country_risk_radar_yearly(risk_data, selected_country)
        return apply_theme(fig)
    except Exception as e:
        print(f"Error updating risk radar: {e}")
        return {}

    
    try:
        from visualizations.tab2_pie_chart import get_pie_viz
        fig = get_pie_viz(risk_data, selected_country, "Total Deaths", selected_year-5, selected_year)
        return fig
    except Exception as e:
        print(f"Error updating disaster pie chart: {e}")
        return {}

@callback(
    Output("economic-bubble-chart", "figure"),
    Output("cluster-chlorepath-title", "children"),
    Input("country-selector", "value"),
    prevent_initial_call=True
)
def update_economic_bubble(selected_country):
    """Update the economic bubble chart based on selected country."""
    if not selected_country:
        return {},"nothing found"
    
    try:
        from visualizations.tab4_cluster_chlorepath import plot_cluster_choropleth_by_risk
        fig, title = plot_cluster_choropleth_by_risk(cluster_data, risk_data, country_name=selected_country)
        return apply_theme(fig), title
    except Exception as e:
        print(f"Error updating economic bubble chart: {e}")
        return {},"nothing found"

    
    try:
        from visualizations.tab2_radar_chart import get_radar_viz
        fig = get_radar_viz(risk_data, selected_country, 2010, 2020)
        return fig
    except Exception as e:
        print(f"Error updating vulnerability radar: {e}")
        return {}

# Region Hotspot Map Callbacks
@callback(
    Output("region-hotspot-map", "figure"),
    Input("country-selector", "options"),
    Input("year-selector", "options")
)
def initialize_region_hotspot_map(country_options, year_options):
    """Initialize the region hotspot map with default data."""
    if not country_options or not year_options or len(country_options) == 0 or len(year_options) == 0:
        return {}
    
    default_country = country_options[0]["value"]
    default_year = year_options[0]["value"]
    
    # Handle "all" year case for initialization
    year_arg = None if default_year == "all" else default_year
    
    try:
        from visualizations.tab4_region_hotspot import plot_disasters_on_map
        fig = plot_disasters_on_map(risk_data, cities_data, default_country, year_arg)
        return apply_theme(fig)
    except Exception as e:
        print(f"Error initializing region hotspot map: {e}")
        return {}

@callback(
    Output("region-hotspot-map", "figure", allow_duplicate=True),
    Input("country-selector", "value"),
    Input("year-selector", "value"),
    Input("map-style-selector", "value"),
    prevent_initial_call=True
)
def update_region_hotspot_map(selected_country, selected_year, map_style):
    """Update the region hotspot map based on selected country, year, and map style. If year is 'all', show all years."""
    if not selected_country:
        return {}
    try:
        from visualizations.tab4_region_hotspot import plot_disasters_on_map
        year_arg = None if selected_year == "all" else selected_year
        fig = plot_disasters_on_map(risk_data, cities_data, selected_country, year_arg, mapbox_style=map_style)
        return apply_theme(fig)
    except Exception as e:
        print(f"Error updating region hotspot map: {e}")
        return {} 

@callback(
    Output("tab4-parallel-plot", "figure"),
    Input("parallel-plot-type-selector", "value"),
    Input("country-selector", "value"),
    Input("year-selector", "value")
)
def update_tab4_parallel_plot(plot_type, selected_country, selected_year):
    """Update the parallel coordinates plot in tab4 based on dropdown and selectors."""
    if not plot_type or not selected_country or not selected_year or risk_data is None:
        return {}
    try:
        from visualizations.tab4_parallel_plot import plot_parallel_coordinates
        # For parallel plot, we can use all data regardless of year selection
        df = index_data
        fig = plot_parallel_coordinates(df, plot_type=plot_type)
        fig.update_layout(height=460, autosize=True)
        return apply_theme(fig)
    except Exception as e:
        print(f"Error updating tab4 parallel plot: {e}")
        return {} 
    

@callback(
    Output("parallel-plot-title", "children"),
    Input("parallel-plot-type-selector", "value")
)
def update_parallel_plot_title(plot_type):
    titles = {
        "risk_vs_outcome": "Risk & Capacity vs Disaster Outcomes",
        "wealth_vs_impact": "Wealth & Health vs Disaster Impact",
        "vulnerability_path": "Vulnerability Pathways"
    }
    return titles.get(plot_type, "Parallel Coordinates Plot")

@callback(
    Output("multi-country-selector", "options"),
    Input("country-selector", "id")
)
def populate_multi_country_dropdown(trigger):
    """Populate the multi-country dropdown with available countries from the risk dataset."""
    if risk_data is None:
        return []
    if 'Country_x' in risk_data.columns:
        countries = sorted(risk_data['Country_x'].dropna().unique())
    else:
        return []
    options = [{"label": country, "value": country} for country in countries]
    return options

@callback(
    Output("country-risk-radar", "figure", allow_duplicate=True),
    Input("multi-country-selector", "value"),
    prevent_initial_call=True
)
def update_multi_country_risk_radar(selected_countries):
    """Update the risk radar chart for multiple countries if selected, else fallback to single-country logic."""
    if not selected_countries:
        return {}
    try:
        from visualizations.tab4_risk_spider import multi_country_risk_radar_with_slider
        # Limit to 4 countries for clarity
        if isinstance(selected_countries, str):
            selected_countries = [selected_countries]
        selected_countries = selected_countries[:4]
        fig = multi_country_risk_radar_with_slider(risk_data, selected_countries)
        return apply_theme(fig)
    except Exception as e:
        print(f"Error updating multi-country risk radar: {e}")
        return {}


@callback(
    Output("tab2_bar_chart", "figure", allow_duplicate=True),
    Input("tab2_bar_chart", "id"),
    # Input("country-selector", "value"),
    # Input("year-selector_2", "value"),
    # Input("map-style-selector", "value"),
    prevent_initial_call=True
)
def update_tab2_barchart():
    # """Update the region hotspot map based on selected country, year, and map style. If year is 'all', show all years."""
    # if not s:
    #     return {}
    try:
        from visualizations.tab2_stacked_area import plot_stacked_disasters_by_year
        fig = plot_stacked_disasters_by_year(risk_data)
        return apply_theme(fig)
    except Exception as e:
        print(f"Error updating region hotspot map: {e}")
        return {} 


@callback(
    Output('wordcloud-img', 'src'),
     Input("country-selector", "value"),
)
def update_wordcloud(selected_country):
    if not selected_country:
        return ''
    from visualizations.tab4_wordclound import generate_location_wordcloud
    return generate_location_wordcloud(risk_data, selected_country)
