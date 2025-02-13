#!/usr/bin/env python3
# *-*- coding: utf-8 -*-
"""Label embeddings."""

import pandas as pd

from src.config import Config
from src.task.reducer import Reducer
from src.vectorstore import LegislationVectorStore


class Labeler:
    """Label embeddings."""

    def __init__(self, config: Config):
        self.config = config
        self.vectorstore = LegislationVectorStore(config)
        self.reducer = Reducer(self.vectorstore)

    def label(self, df: pd.DataFrame) -> pd.DataFrame:
        """Label the embeddings with topic tags."""
        # Query topics and process results
        results = self.vectorstore.collection.query(
            query_texts=self.config.topics, n_results=10
        )
        for topic_idx, result in enumerate(results["ids"]):
            topic = self.config.topics[topic_idx]
            for idx in result:
                # Update the dataframe topic column where the id matches
                df.loc[df["id"] == idx, topic] = 1
        df[self.config.topics] = df[self.config.topics].fillna(0)
        return df


def main():
    config = Config()
    labeler = Labeler(config)
    if not (config.out_dir / "reduced_embeddings.csv").exists():
        reducer = Reducer()
        reducer.process()
        df = reducer.data_frame
    else:
        df = pd.read_csv(config.out_dir / "reduced_embeddings.csv")
    df = labeler.label(df)
    df.to_csv(config.out_dir / "labeled_embeddings.csv", index=False)
