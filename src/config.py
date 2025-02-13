#!/usr/bin/env python3
# *-*- coding: utf-8 -*-
"""Configuration utilities."""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

TOPICS = [
    "agriculture",
    "economy",
    "education",
    "energy",
    "environment",
    "health",
    "housing",
    "immigration",
    "infrastructure",
    "national security",
    "social security",
    "transportation",
    "veterans",
]


class Config(BaseSettings):
    """Configuration class."""

    model_config = SettingsConfigDict(cli_parse_args=True)

    db_dir: str = "embeddings"
    data_dir: Path = "data"
    out_dir: Path = "out"
    batch_size: int = 100
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_workers: int = 4
    limit: int = 10000
    topics: List[str] = TOPICS
    query: str = "Judiciary"
