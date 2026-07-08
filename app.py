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

# Full-screen loading bar shown while the Dash bundle downloads and the layout
# first renders. It sits in the initial HTML shell (so it appears instantly) and
# removes itself once the real layout (#app-container) has mounted.
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            #boot-loader {
                position: fixed; inset: 0; z-index: 99999;
                display: flex; flex-direction: column;
                align-items: center; justify-content: center; gap: 22px;
                background: #0d0d0d; color: #ffffff;
                font-family: 'Space Grotesk', system-ui, -apple-system, sans-serif;
                transition: opacity .55s ease, visibility .55s ease;
            }
            #boot-loader.boot-loader--hidden {
                opacity: 0; visibility: hidden; pointer-events: none;
            }
            .boot-loader__brand { text-align: center; }
            .boot-loader__title { font-size: 26px; font-weight: 700; letter-spacing: .3px; }
            .boot-loader__sub {
                margin-top: 8px; font-size: 12px; color: #898781;
                letter-spacing: .16em; text-transform: uppercase;
            }
            .boot-loader__track {
                position: relative; width: min(360px, 72vw); height: 6px;
                border-radius: 999px; background: #1a1a19; overflow: hidden;
                box-shadow: inset 0 0 0 1px #2c2c2a;
            }
            .boot-loader__fill {
                position: absolute; inset: 0 auto 0 0; width: 8%;
                border-radius: 999px; transition: width .2s ease;
                background: linear-gradient(90deg, #3987e5, #9085e9);
            }
            .boot-loader__pct {
                font-size: 12px; color: #c3c2b7; font-variant-numeric: tabular-nums;
            }
        </style>
    </head>
    <body>
        <div id="boot-loader">
            <div class="boot-loader__brand">
                <div class="boot-loader__title">Global Natural Disasters</div>
                <div class="boot-loader__sub">Loading visualizations</div>
            </div>
            <div class="boot-loader__track"><div id="boot-loader__fill" class="boot-loader__fill"></div></div>
            <div id="boot-loader__pct" class="boot-loader__pct">8%</div>
        </div>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <script>
        (function () {
            var overlay = document.getElementById('boot-loader');
            if (!overlay) return;
            var fill = document.getElementById('boot-loader__fill');
            var pct  = document.getElementById('boot-loader__pct');
            var progress = 8, done = false;

            var tick = setInterval(function () {
                if (done) return;
                progress += Math.max(0.4, (90 - progress) * 0.06);
                if (progress > 90) progress = 90;
                fill.style.width = progress.toFixed(1) + '%';
                pct.textContent = Math.round(progress) + '%';
            }, 120);

            function finish() {
                if (done) return;
                done = true;
                clearInterval(tick);
                fill.style.width = '100%';
                pct.textContent = '100%';
                overlay.classList.add('boot-loader--hidden');
                setTimeout(function () {
                    if (overlay && overlay.parentNode) overlay.parentNode.removeChild(overlay);
                }, 650);
            }

            // The real layout mounts as #app-container — finish shortly after.
            var watch = setInterval(function () {
                if (document.getElementById('app-container')) {
                    clearInterval(watch);
                    setTimeout(finish, 350);
                }
            }, 100);

            // Safety valve: never trap the user behind the loader.
            setTimeout(finish, 60000);
        })();
        </script>
    </body>
</html>
"""

app.layout = layout

# WSGI entry point for production servers (e.g. `gunicorn app:server` on Render)
server = app.server

if __name__ == "__main__":
    # Local development server. In production the app is served via `server` above.
    import os

    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8065)))
