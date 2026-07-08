# Global Natural Disasters — An Interactive Visualization Portal

An interactive web dashboard for exploring a century of global natural-disaster
data — human losses, economic damage, and country-level vulnerability — built
with [Dash](https://dash.plotly.com/) and [Plotly](https://plotly.com/python/).

The portal brings together disaster-event records, economic-impact figures, and
~50 country risk indicators into a single explorable interface, so patterns
across disaster type, geography, and time can be examined side by side.

## Features

The dashboard is organised into seven tabs:

| Tab | What it shows |
| --- | --- |
| **Overview & Global Patterns** | World choropleth and high-level summaries of disaster impact across countries and time, driven by a year slider. |
| **Disaster Type Analysis** | Breakdown by disaster type — bar, pie, radar, Sankey and stacked-area views of how different hazards contribute to impact. |
| **Economic Impact & Vulnerability** | Economic losses over time, plus bubble/scatter/lollipop comparisons of damage against wealth and exposure. |
| **Country Risk Profiles** | Per-country deep dive — risk radar, hotspot maps, parallel-coordinate and word-cloud summaries of a country's risk profile. |
| **Risk Clusters (UMAP)** | Countries projected from ~50 risk indicators into 2-D with UMAP; nearby countries share a similar risk profile. Click a point to profile its cluster. |
| **Trends & Correlations** | Rolling correlations, correlation matrices, scatter matrices, multi-metric trends and a correlation network between metrics and disaster types. |
| **Data & Sources** | Provenance and links for every dataset used. |

## Tech stack

- **Python 3.9+**
- **Dash** and **Plotly** for the app and charts
- **pandas** / **numpy** for data wrangling
- **scikit-learn** + **umap-learn** for the risk-cluster projection
- **networkx** for the correlation network, **wordcloud** for country summaries
- **pycountry** / **fuzzywuzzy** for country-name normalisation

## Getting started

```bash
# 1. Clone
git clone https://github.com/ashutoshanandmehta/Global-Natural-Disasters-An-Interactive-Visualization-Portal.git
cd Global-Natural-Disasters-An-Interactive-Visualization-Portal

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python app.py
```

Then open <http://127.0.0.1:8065> in your browser.


## Deployment (Render)

This app is a long-running Dash/Flask server and is deployed on
[Render](https://render.com/). The repo ships everything Render needs:

- `server = app.server` in `app.py` — the WSGI entry point
- `render.yaml` — infrastructure blueprint (build/start commands, Python version)
- `Procfile` and `runtime.txt` — for a manual (dashboard) setup

**Deploy in a few clicks:**

1. Push this repo to GitHub (already done).
2. On the [Render dashboard](https://dashboard.render.com/), choose
   **New → Blueprint** and select this repository. Render reads `render.yaml`
   and provisions the web service automatically.
   *(Or **New → Web Service** and let it auto-detect: build
   `pip install -r requirements.txt`, start
   `gunicorn app:server --bind 0.0.0.0:$PORT`.)*
3. Click **Deploy**. Render installs the dependencies and starts gunicorn; the
   app comes up at `https://<your-service>.onrender.com`.

> The free plan spins the service down after inactivity, so the first request
> after idle takes a few extra seconds to wake it.

## Project structure

```
app.py                 # Dash entry point (registers layout + callbacks)
callbacks.py           # Interactive callbacks for most tabs
callbacks_extra.py     # Overview + Risk Clusters (UMAP) callbacks
ui/                    # Layout, components and theme
visualizations/        # One module per chart, grouped by tab
preprocessing/         # Data-preparation and UMAP scripts
data/                  # Raw datasets, risk analysis and processed CSVs
assets/                # CSS and JavaScript
```

## Data sources

- **Our World in Data** — natural disasters (ourworldindata.org/natural-disasters)
- **EM-DAT** — international disaster database, CRED / UCLouvain (emdat.be)
- **WorldRiskReport** — risk and vulnerability indicators (weltrisikobericht.de)
- **Countries States Cities Database** — geo reference data (github.com/dr5hn)

## Acknowledgements

Built as a course project for **CS661 — Big Data Visual Analytics**.
