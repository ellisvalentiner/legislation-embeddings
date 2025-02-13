#!/usr/bin/env python3
# *-*- coding: utf-8 -*-
"""Visualize embeddings."""

import pandas as pd
import plotly.express as px
from inflection import titleize

from src.config import TOPICS, Config


def main():
    config = Config()
    df = pd.read_csv(config.out_dir / "labeled_embeddings.csv")
    columns_with_1 = df[TOPICS].eq(1).apply(lambda row: row.index[row].tolist(), axis=1)
    df["Topic"] = (
        columns_with_1.apply(lambda x: x[0] if x else None)
        .fillna("other")
        .apply(titleize)
    )
    fig = px.scatter(
        data_frame=df,
        x="0",
        y="1",
        color="Topic",
        color_discrete_map={"Other": "#c3c3c3"},
        labels={"0": "Dimension 1", "1": "Dimension 2"},
        title="UMAP Legislation Embeddings",
    )
    fig.write_image(
        config.out_dir / f"fig-{config.color}.png", width=800, height=600, scale=2
    )
