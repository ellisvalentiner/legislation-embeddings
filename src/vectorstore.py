#!/usr/bin/env python3
# *-*- coding: utf-8 -*-
"""Chroma utilities."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import numpy as np
import pandas as pd
from chromadb import PersistentClient
from chromadb.api.types import IncludeEnum

from src.config import Config


class LegislationVectorStore:
    def __init__(self, config: Config = Config()):
        self.client = PersistentClient(config.db_dir.name)
        self.collection = self.client.create_collection(
            name="legislation", get_or_create=True
        )
        self.db_dir = Path(config.db_dir)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database."""
        with sqlite3.connect(self.db_dir / "chroma.sqlite3") as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS processed_files (
                    file_path TEXT PRIMARY KEY,
                    file_signature TEXT,
                    processed_at TIMESTAMP,
                    metadata TEXT
                )
            """
            )

    @staticmethod
    def get_file_signature(file_path: Path) -> str:
        """Generate a quick file signature using metadata.

        Args:
            file_path: Path to the file

        Returns:
            A string combining size and modification time
        """
        stat = file_path.stat()
        return f"{stat.st_size}_{stat.st_mtime_ns}"

    # noinspection SqlResolve
    def is_processed(self, file_path: Path) -> bool:
        """Check if a file has been processed.

        Args:
            file_path: Path to the file

        Returns:
            True if the file has been processed, False otherwise
        """
        current_hash = self.get_file_signature(file_path)
        with sqlite3.connect(self.db_dir / "chroma.sqlite3") as conn:
            cursor = conn.execute(
                "SELECT file_signature FROM processed_files WHERE file_path = ?",
                (str(file_path),),
            )
            result = cursor.fetchone()
            return result is not None and result[0] == current_hash

    def mark_file_processed(self, file_path: Path, metadata: Dict[str, Any]) -> None:
        """Mark file as processed in state database.

        Args:
            file_path: Path to the file
            metadata: Metadata associated with the file

        Returns:
            None
        """
        current_signature = self.get_file_signature(file_path)

        with sqlite3.connect(self.db_dir / "chroma.sqlite3") as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO processed_files 
                (file_path, file_signature, processed_at, metadata) 
                VALUES (?, ?, ?, ?)
                """,
                (
                    str(file_path),
                    current_signature,
                    datetime.now().isoformat(),
                    str(metadata),
                ),
            )
