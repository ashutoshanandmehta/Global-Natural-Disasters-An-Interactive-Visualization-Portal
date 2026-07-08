# compute_umap.py
#
# Offline pre-processing step (run once): reduces the high-dimensional
# World Risk Index metrics for every country-year into a 2D UMAP embedding,
# joins the pre-computed K-Means cluster labels, and saves the result to
# data/processed/umap_embedding.csv for the dashboard's Risk Clusters tab.
#
# Pipeline:  ~50 risk indicators  ->  StandardScaler  ->  UMAP(2D)  ->  CSV
#
# Usage:  .venv/bin/python preprocessing/compute_umap.py

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import umap

ROOT = Path(__file__).resolve().parents[1]
RISK_CSV = ROOT / "data" / "Risk_Analysis" / "risk_data.csv"
CLUSTER_CSV = ROOT / "data" / "Risk_Analysis" / "risk_data_clustered.csv"
OUT_CSV = ROOT / "data" / "processed" / "umap_embedding.csv"

# The six composite World Risk Index dimensions plus their published
# sub-scores — the "high-dimensional risk metrics" being reduced.
FEATURE_COLS = [
    "W", "E", "V", "S", "C", "A",
    "S_01", "S_02", "S_03", "S_04", "S_05",
    "C_01", "C_02", "C_03",
    "A_01", "A_02", "A_03",
    "EI_01", "EI_02", "EI_03", "EI_04", "EI_05", "EI_06", "EI_07",
    "SI_01", "SI_02", "SI_03", "SI_04", "SI_05", "SI_06", "SI_07",
    "SI_08", "SI_09", "SI_10", "SI_11", "SI_12", "SI_13", "SI_14",
    "CI_01", "CI_02", "CI_03", "CI_04", "CI_05", "CI_06", "CI_07",
    "AI_01", "AI_02", "AI_03", "AI_04",
]


def main():
    risk = pd.read_csv(RISK_CSV)
    clusters = pd.read_csv(CLUSTER_CSV)

    features = [c for c in FEATURE_COLS if c in risk.columns]
    df = risk[["WRI.Country", "ISO3.Code", "Year"] + features].copy()
    df[features] = df[features].apply(pd.to_numeric, errors="coerce")

    # Drop rows with too many missing indicators, median-impute the rest
    df = df[df[features].notna().mean(axis=1) >= 0.8].reset_index(drop=True)
    df[features] = df[features].fillna(df[features].median())

    X = StandardScaler().fit_transform(df[features].to_numpy(dtype=float))

    reducer = umap.UMAP(
        n_components=2,
        n_neighbors=15,
        min_dist=0.1,
        metric="euclidean",
        random_state=42,
    )
    embedding = reducer.fit_transform(X)

    out = pd.DataFrame(
        {
            "country": df["WRI.Country"],
            "iso_code": df["ISO3.Code"],
            "year": df["Year"].astype(int),
            "umap_x": np.round(embedding[:, 0], 4),
            "umap_y": np.round(embedding[:, 1], 4),
            # Carry the headline metrics for hover tooltips
            "wri": df["W"],
            "exposure": df["E"],
            "vulnerability": df["V"],
            "susceptibility": df["S"],
            "coping_deficit": df["C"],
            "adaptation_deficit": df["A"],
        }
    )

    clusters = clusters.rename(columns={"iso_code": "iso_code", "year": "year"})
    out = out.merge(
        clusters[["iso_code", "year", "cluster"]],
        on=["iso_code", "year"],
        how="left",
    )
    out["cluster"] = out["cluster"].fillna(-1).astype(int)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False)
    print(f"Wrote {len(out)} rows ({out['country'].nunique()} countries, "
          f"{out['year'].min()}-{out['year'].max()}) -> {OUT_CSV}")
    print(out["cluster"].value_counts().sort_index())


if __name__ == "__main__":
    main()
