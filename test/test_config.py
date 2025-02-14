#!/usr/bin/env python3
# *-*- coding: utf-8 -*-
"""Test configuration."""
import sys

from src.config import Config


class TestConfig:
    def test_config(self):
        config = Config(max_workers=4)
        assert config.batch_size == 100
        assert config.max_workers == 4
        assert config.limit == 10000
        assert config.topics == [
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
        assert config.query == "Judiciary"

    def test_config_cli(self):
        sys.argv = ["config.py", "--limit", "10"]
        config = Config()
        assert config.limit == 10
