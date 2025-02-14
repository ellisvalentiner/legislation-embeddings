#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Search"""

from typing import Any, Mapping

from chromadb import QueryResult

from src.config import Config
from src.vectorstore import LegislationVectorStore


def search(
    query: str = "",
    vectorstore: LegislationVectorStore = LegislationVectorStore(),
    limit: int = 5,
) -> list[Any] | list[Mapping[str, str | int | float | bool]]:
    """Search the vector store for similar legislation.

    Args:
        query: The query string to search for
        vectorstore: The vector store to search
        limit: The maximum number of results to return

    Returns:
        A list of similar legislation
    """
    results: QueryResult = vectorstore.collection.query(
        query_texts=[query], n_results=limit
    )
    metadatas = results.get("metadatas", [])
    if not metadatas:
        return []
    return [_ for r in metadatas for _ in r]


def main():
    config = Config()
    for result in search(query=config.query):
        print(result["dc_title"])
