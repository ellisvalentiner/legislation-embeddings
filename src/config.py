#!/usr/bin/env python3
# *-*- coding: utf-8 -*-
"""Configuration utilities."""

from pathlib import Path
from typing import List
from multiprocessing import cpu_count

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

    db_dir: Path = Path("embeddings")
    data_dir: Path = Path("data")
    out_dir: Path = Path("out")
    batch_size: int = 100
    max_workers: int = cpu_count()
    limit: int = 10000
    topics: List[str] = TOPICS
    query: str = "Judiciary"
