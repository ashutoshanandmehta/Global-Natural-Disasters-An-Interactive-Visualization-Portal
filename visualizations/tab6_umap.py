# tab6_umap.py
# Risk Clusters tab: renders the pre-computed 2D UMAP embedding of ~50
# World Risk Index indicators per country-year (see preprocessing/compute_umap.py)
# and a per-cluster profile chart across the six composite risk dimensions.

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from ui.theme import CLUSTER_COLORS, INK, INK_2, INK_MUTED, HAIRLINE

EMBEDDING_CSV = (
    Path(__file__).resolve().parents[1] / "data" / "processed" / "umap_embedding.csv"
)

DIMENSIONS = {
    "exposure": "Exposure",
    "vulnerability": "Vulnerability",
    "susceptibility": "Susceptibility",
    "coping_deficit": "Lack of coping capacity",
    "adaptation_deficit": "Lack of adaptive capacity",
}


def load_embedding() -> pd.DataFrame:
    return pd.read_csv(EMBEDDING_CSV)


def cluster_labels(df: pd.DataFrame) -> dict:
    """Readable name per cluster from its mean exposure/vulnerability profile,
    judged against the other clusters (not against raw point medians)."""
    labels = {}
    means = (df[df["cluster"] >= 0]
             .groupby("cluster")[["exposure", "vulnerability"]].mean())
    e_mid = means["exposure"].median()
    v_mid = means["vulnerability"].median()
    for c, row in means.iterrows():
        e = "high" if row["exposure"] >= e_mid else "low"
        v = "high" if row["vulnerability"] >= v_mid else "low"
        labels[int(c)] = f"Cluster {int(c)} — {e} exposure · {v} vulnerability"
    labels[-1] = "Unclustered"
    return labels


def get_umap_scatter(df, year=None, highlight_country=None):
    """2D UMAP embedding, one point per country-year, colored by risk cluster."""
    data = df if year in (None, "all") else df[df["year"] == int(year)]
    labels = cluster_labels(df)

    fig = go.Figure()
    for c in sorted(data["cluster"].unique()):
        grp = data[data["cluster"] == c]
        fig.add_trace(go.Scatter(
            x=grp["umap_x"], y=grp["umap_y"],
            mode="markers",
            name=labels.get(int(c), f"Cluster {c}"),
            marker=dict(
                size=5 if year in (None, "all") else 9,
                color=CLUSTER_COLORS.get(int(c), "#898781"),
                opacity=0.45 if year in (None, "all") else 0.8,
                line=dict(width=0),
            ),
            customdata=grp[["country", "year", "wri", "exposure",
                            "vulnerability", "cluster"]],
            hovertemplate=(
                "<b>%{customdata[0]}</b> · %{customdata[1]}<br>"
                "World Risk Index %{customdata[2]:.1f}<br>"
                "Exposure %{customdata[3]:.1f} · Vulnerability %{customdata[4]:.1f}"
                "<extra>%{fullData.name}</extra>"
            ),
        ))

    if highlight_country:
        # Always trace the country's full 2000-2024 trajectory, even when a
        # single year is selected — the path is the interesting part.
        hl = df[df["country"] == highlight_country].sort_values("year")
        if not hl.empty:
            fig.add_trace(go.Scatter(
                x=hl["umap_x"], y=hl["umap_y"],
                mode="lines+markers+text",
                name=highlight_country,
                text=[str(y) if y in (hl["year"].min(), hl["year"].max())
                      else "" for y in hl["year"]],
                textposition="top center",
                textfont=dict(size=10, color=INK),
                line=dict(width=1, color=INK, dash="dot"),
                marker=dict(
                    size=11, color="rgba(0,0,0,0)",
                    line=dict(width=2, color=INK),
                ),
                customdata=hl[["country", "year", "wri", "exposure",
                               "vulnerability", "cluster"]],
                hovertemplate=(
                    "<b>%{customdata[0]}</b> · %{customdata[1]}<br>"
                    "World Risk Index %{customdata[2]:.1f}"
                    "<extra>highlighted</extra>"
                ),
            ))

    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0,
                    itemsizing="constant"),
        xaxis=dict(title="UMAP dimension 1", showgrid=False, zeroline=False,
                   showticklabels=False),
        yaxis=dict(title="UMAP dimension 2", showgrid=False, zeroline=False,
                   showticklabels=False),
        dragmode="pan",
    )
    return fig


def get_cluster_profile(df, cluster=None):
    """Mean score per risk dimension — all clusters, or one vs. global mean."""
    valid = df[df["cluster"] >= 0]
    labels = cluster_labels(df)
    dims = list(DIMENSIONS.keys())
    dim_names = list(DIMENSIONS.values())

    fig = go.Figure()
    if cluster is None or int(cluster) < 0:
        for c, grp in valid.groupby("cluster"):
            fig.add_trace(go.Bar(
                x=grp[dims].mean().values, y=dim_names,
                orientation="h",
                name=labels[int(c)].split(" — ")[0],
                marker=dict(color=CLUSTER_COLORS.get(int(c)),
                            cornerradius=4),
                hovertemplate="%{y}: %{x:.1f}<extra>%{fullData.name}</extra>",
            ))
        fig.update_layout(barmode="group", bargap=0.25, bargroupgap=0.12,
                          title=dict(text="Average score per cluster"))
    else:
        c = int(cluster)
        grp = valid[valid["cluster"] == c]
        fig.add_trace(go.Bar(
            x=grp[dims].mean().values, y=dim_names,
            orientation="h",
            name=labels.get(c, f"Cluster {c}"),
            marker=dict(color=CLUSTER_COLORS.get(c), cornerradius=4),
            hovertemplate="%{y}: %{x:.1f}<extra></extra>",
        ))
        fig.add_trace(go.Bar(
            x=valid[dims].mean().values, y=dim_names,
            orientation="h",
            name="All countries",
            marker=dict(color="#4a4a47", cornerradius=4),
            hovertemplate="%{y}: %{x:.1f}<extra>global mean</extra>",
        ))
        fig.update_layout(
            barmode="group", bargap=0.3, bargroupgap=0.15,
            title=dict(text=labels.get(c, f"Cluster {c}")),
        )

    fig.update_layout(
        xaxis=dict(title="Mean score (0–100)", range=[0, 100]),
        yaxis=dict(autorange="reversed"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, x=0),
    )
    return fig
