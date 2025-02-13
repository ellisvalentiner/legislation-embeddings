#!/usr/bin/env python3
# *-*- coding: utf-8 -*-
"""Test XML."""
import pytest
from pathlib import Path
from src.xml import XMLParser


class TestXMLParser:

    def test_init(self):
        parser = XMLParser()
        assert parser.namespaces == {"dc": "http://purl.org/dc/elements/1.1/"}

    def test_parse_file(self):
        parser = XMLParser()
        result = parser.parse_file(Path("test/fixtures/BILLS-117hres24rds.xml"))
        assert result["dms_id"] == "H862E24D6792446E1AF1CAA15EEADC5CF"
        assert result["public_private"] == "public"
        assert (
            result["dc_title"]
            == "117 HRES 24 : Impeaching Donald John Trump, President of the United States, for high crimes and misdemeanors."
        )
        assert result["dc_publisher"] == "U.S. House of Representatives"
        assert result["dc_date"] == "2021-01-13"
        assert result["dc_format"] == "text/xml"
        assert result["dc_language"] == "EN"
        assert (
            result["dc_rights"]
            == "Pursuant to Title 17 Section 105 of the United States Code, this file is not subject to copyright protection and is in the public domain."
        )
