# app.py
from dash import Dash
from ui.layout import layout
import callbacks        # Import callbacks to register them
import callbacks_extra  # Overview + Risk Clusters (UMAP) callbacks

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&display=swap",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css",
    ],
)
app.title = "Global Natural Disasters — Visualization Portal"
app.layout = layout

if __name__ == "__main__":
    app.run(debug=True, port=8065)
