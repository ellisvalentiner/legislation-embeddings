#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Search"""

from typing import Any, Dict, List

from src.config import Config
from src.vectorstore import LegislationVectorStore


def search(
    query: str = "",
    vectorstore: LegislationVectorStore = LegislationVectorStore(),
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """Search the vector store for similar legislation.

    Args:
        query: The query string to search for
        vectorstore: The vector store to search
        limit: The maximum number of results to return

    Returns:
        A list of similar legislation
    """
    results = vectorstore.collection.query(query_texts=[query], n_results=limit)
    return [_ for r in results["metadatas"] for _ in r]


def main():
    config = Config()
    for result in search(query=config.query):
        print(result["dc_title"])
