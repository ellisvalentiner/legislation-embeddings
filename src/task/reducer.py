#!/usr/bin/env python3
# *-*- coding: utf-8 -*-
"""Reducer job and utilities."""

from typing import List, Optional, Union

import numpy as np
import pandas as pd
import umap
from chromadb.api.types import IncludeEnum, Embeddings, PyEmbeddings, NDArray, Metadata

from src.config import Config
from src.vectorstore import LegislationVectorStore


class Reducer:
    """Reduce dimensionality of embeddings for visualization."""

    def __init__(
        self,
        vectorstore: LegislationVectorStore = LegislationVectorStore(config=Config()),
        reducer=umap.UMAP(n_neighbors=10, n_components=2, min_dist=0.0),
    ):
        self.vectorstore: LegislationVectorStore = vectorstore
        self.reducer = reducer
        self.ids: List[str] = []
        self.metadatas: Optional[List[Metadata]] = []
        self.embeddings: Optional[
            Union[Embeddings, PyEmbeddings, NDArray[Union[np.int32, np.float32]]]
        ] = []
        self.reduced_embeddings: List[List[float]] = []

    def process(self):
        """Process the vector store and generate PCA."""
        # Load embeddings from vectorstore if not already loaded
        if not self.embeddings:
            self.load_from_vectorstore()
        self.reduced_embeddings = self.reducer.fit_transform(self.embeddings)

    def load_from_vectorstore(self):
        result = self.vectorstore.collection.get(
            include=[IncludeEnum.metadatas, IncludeEnum.embeddings]
        )
        self.ids = result["ids"]
        self.metadatas = result["metadatas"]
        self.embeddings = result["embeddings"]

    @property
    def data_frame(self):
        if self.reduced_embeddings is None:
            self.reduced_embeddings = self.reducer.fit_transform(self.embeddings)
        df = pd.DataFrame(self.reduced_embeddings)
        df["id"] = self.ids
        if self.metadatas is not None:
            for k in self.metadatas[0].keys():
                df[k] = [m.get(k) for m in self.metadatas]
        return df


def main():
    config = Config()
    vectorstore = LegislationVectorStore(config=config)
    job = Reducer(vectorstore=vectorstore)
    job.process()
    job.data_frame.to_csv(config.out_dir / "reduced_embeddings.csv", index=False)
