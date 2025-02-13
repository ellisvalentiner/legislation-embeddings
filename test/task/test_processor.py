#!/usr/bin/env python3
# *-*- coding: utf-8 -*
from src.task.processor import BatchProcessor, DataProcessor


class TestBatchProcessor:

    def test_process_files(self):
        processor = BatchProcessor()
        result = processor.process_files(["test/fixtures/BILLS-117hres24rds.xml"], lambda x: x)
        assert result == result
