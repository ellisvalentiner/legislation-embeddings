#!/usr/bin/env python3
# *-*- coding: utf-8 -*-
"""Data processing utilities."""

import random
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, Any, Optional

from src.config import Config
from src.logging import logger
from src.vectorstore import LegislationVectorStore
from src.xml import XMLParser


class BatchProcessor:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers

    def process_files(self, files: list[Path], process_fn: callable) -> list[Any]:
        """Process a list of files in parallel.

        Args:
            files: List of files to process
            process_fn: Function to process each file

        Returns:
            List of results from processing each file
        """
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(process_fn, files))


class DataProcessor:
    def __init__(self, config: Config = Config()):
        self.data_dir = Path(config.data_dir)
        self.xml_parser = XMLParser()
        self.batch_processor = BatchProcessor(max_workers=config.max_workers)
        self.vectorstore = LegislationVectorStore(config=config)
        self.batch_size = config.batch_size
        self.limit = config.limit

    def process_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Process a single file with error handling.

        Args:
            file_path: Path to the file

        Returns:
            Metadata associated with the file
        """
        if self.vectorstore.is_processed(file_path):
            logger.debug("Skipping processed file", extra={"file_path": file_path})
            return None

        try:
            # Parse XML metadata
            result = self.xml_parser.parse_file(file_path)
            if result:
                # Mark file as processed
                self.vectorstore.mark_file_processed(file_path, result)
                return result
            return None
        except Exception as e:
            logger.error(
                "Error processing file path", extra={"file_path": file_path}, exc_info=e
            )
            return None

    # noinspection SqlResolve
    def get_processing_status(self) -> Dict[str, Any]:
        """Get processing status statistics.

        Returns:
            Processing status statistics
        """
        with sqlite3.connect(self.vectorstore.db_dir / "chroma.sqlite3") as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM processed_files")
            processed_count = cursor.fetchone()[0]

            total_files = len(list(self.data_dir.glob("*.xml")))

            return {
                "total_files": total_files,
                "processed_files": processed_count,
                "remaining_files": total_files - processed_count,
                "progress_percentage": (
                    (processed_count / total_files * 100) if total_files > 0 else 0
                ),
            }

    def process_batch(self, files: list[Path]) -> None:
        """Process a batch of files and add to vector store.

        Args:
            files: List of files to process

        Returns:
            None
        """

        # Process files in parallel
        results = self.batch_processor.process_files(files, self.process_file)

        # Filter out None results and process valid ones
        valid_results = list(filter(None, results))

        if not valid_results:
            logger.warning("No valid results in batch")
            return

        self.vectorstore.collection.add(
            documents=[_["text"] for _ in valid_results],
            metadatas=[
                {k: v for k, v in d.items() if k != "text"} for d in valid_results
            ],
            ids=[m["file_name"] for m in valid_results],
        )

    def process_all(self, prefix: str = "", limit: int = 0) -> None:
        """Process all XML files in the bills directory.

        Returns:
            None
        """
        if not limit:
            limit = self.limit
        files = list(self.data_dir.glob(f"{prefix}*.xml"))
        if limit:
            # Randomly select a subset of files
            random.shuffle(files)
            files = files[:limit]
        total_files = len(files)
        logger.info("Found XML files to process", extra={"total-files": total_files})

        # Process in batches
        for i in range(0, total_files, self.batch_size):
            batch = files[i : i + self.batch_size]
            self.process_batch(batch)
            logger.info(
                "Processed batch",
                extra={
                    "batch-size": self.batch_size,
                    "total-files": total_files,
                    "batch-index": i,
                },
            )

        # Persist the vector store
        logger.info("Processing complete")


def main():
    config = Config()
    processor = DataProcessor(config=config)

    # Print initial status
    status = processor.get_processing_status()
    logger.info("Initial status", extra={"status": status})

    try:
        processor.process_all()
    except KeyboardInterrupt:
        logger.info("Processing interrupted. Progress has been saved.")
        status = processor.get_processing_status()
        logger.info("Final status", extra={"status": status})
    except Exception as e:
        logger.error("Error during processing", extra={"error": str(e)})
        raise


if __name__ == "__main__":
    main()
