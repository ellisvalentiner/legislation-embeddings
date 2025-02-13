#!/usr/bin/env python3
# *-*- coding: utf-8 -*-
"""Outliers."""

import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.neighbors import NearestNeighbors

from src.config import Config


def find_most_isolated_points(df, n=5, k_neighbors=2):
    # Initialize NearestNeighbors with k neighbors
    nn = NearestNeighbors(n_neighbors=k_neighbors)
    nn.fit(df[["0", "1"]])

    # Find distances to k nearest neighbors
    distances, _ = nn.kneighbors()

    # Calculate isolation score as average distance to k nearest neighbors
    isolation_scores = distances.mean(axis=1)

    # Get indices of top n most isolated points
    most_isolated_idx = np.argsort(isolation_scores)[-n:][::-1]

    return df.iloc[most_isolated_idx]


def main():
    config = Config()
    df = pd.read_csv(config.out_dir / "labeled_embeddings.csv")
    outliers = find_most_isolated_points(df)
    df["Outlier"] = "Other"
    df.loc[outliers.index, "Outlier"] = "Outlier"
    fig = px.scatter(
        data_frame=df,
        x="0",
        y="1",
        color="Outlier",
        color_discrete_map={"Other": "#c3c3c3"},
        color_continuous_scale=px.colors.sequential.Plasma,
        labels={"0": "Dimension 1", "1": "Dimension 2"},
        title="UMAP Legislation Embeddings",
    )
    fig.write_image(config.out_dir / "fig-isolated.png", width=800, height=600, scale=2)
    for _, outlier in outliers.iterrows():
        print(outlier["dc_title"])
