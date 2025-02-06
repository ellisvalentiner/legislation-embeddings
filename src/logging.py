#!/usr/bin/env python3
# *-*- coding: utf-8 -*-
"""Logging utilities."""
import logging

from pythonjsonlogger.json import JsonFormatter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter(timestamp=True))

logger.addHandler(handler)
