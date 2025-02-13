#!/usr/bin/env python3
# *-*- coding: utf-8 -*-
"""XML parsing utilities."""

from pathlib import Path
from typing import Dict, Optional, Any
from lxml import etree as ElementTree
from lxml.etree import Element

from inflection import underscore

from src.logging import logger


class XMLParser:
    def __init__(self):
        self.namespaces = {"dc": "http://purl.org/dc/elements/1.1/"}

    @staticmethod
    def extract_legislation_attributes(root: Element) -> Dict[str, str]:
        """Extract attributes from the root element of a legislation XML file.

        Args:
            root: Root element of the legislation XML file

        Returns:
            A dictionary of attributes extracted from the root element
        """
        elements = ["bill-stage", "bill-type", "dms-id", "public-private"]
        return {underscore(key): root.get(key, "") for key in elements}

    def extract_form_info(self, form: Optional[Element]) -> Dict[str, str]:
        """Extract attributes from the form element of a legislation XML file.

        Args:
            form: Form element of the legislation XML file

        Returns:
            A dictionary of attributes extracted from the form element
        """
        if form is None:
            return self._get_empty_form_info()

        elements = [
            "action-date",
            "action-desc",
            "action-instruction",
            "committee-name",
            "congress",
            "cosponsor",
            "current-chamber",
            "distribution-code",
            "legis-num",
            "legis-type",
            "official-title",
            "session",
            "sponsor",
        ]
        d = {}
        for item in form.iter():
            if item.tag in elements:
                if item.tag in d:
                    d[underscore(item.tag)] = "|".join(
                        [d[underscore(item.tag)], item.text]
                    )
                else:
                    d[underscore(item.tag)] = item.text
        return d

    def extract_dublin_core(self, root: Element) -> Dict[str, str]:
        """Extract attributes from the Dublin Core namespace of a legislation XML file.

        Args:
            root: Root element of the legislation XML file

        Returns:
            A dictionary of attributes extracted from the Dublin Core namespace
        """
        elements = ["title", "publisher", "date", "format", "language", "rights"]
        return {
            f"dc_{elem}": (
                root.find(f".//dc:{elem}", self.namespaces).text
                if root.find(f".//dc:{elem}", self.namespaces) is not None
                else ""
            )
            for elem in elements
        }

    @staticmethod
    def _get_empty_form_info() -> Dict[str, str]:
        """Return empty form information structure."""
        return {
            "distribution_code": "",
            "congress": "",
            "session": "",
            "legis_num": "",
            "current_chamber": "",
            "legis_type": "",
            "official_title": "",
        }

    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse XML file and extract all relevant information."""
        try:
            tree = ElementTree.parse(file_path)
            root = tree.getroot()

            # Get bill attributes
            bill_info = self.extract_legislation_attributes(root)

            # Get form information
            form = root.find(".//form")
            form_info = self.extract_form_info(form)

            # Get Dublin Core metadata
            dc_info = self.extract_dublin_core(root)

            # Extract text content
            text_content = self.extract_text_content(root)

            # Combine all dictionaries and filter out None values
            combined_dict = {
                **bill_info,
                **form_info,
                **dc_info,
                "text": text_content,
                "source": str(file_path),
                "file_name": file_path.name,
            }

            # Return dictionary with non-None values only
            return {k: v for k, v in combined_dict.items() if v is not None}
        except Exception as e:
            logger.error(
                "Error parsing XML file", extra={"file_path": file_path}, exc_info=e
            )
            return {}

    @staticmethod
    def extract_text_content(root: Element) -> str:
        """Extract text content from the XML.

        Args:
            root: Root element of the legislation XML file

        Returns:
            A string containing the text content of the legislation
        """
        # Get all text elements, removing extra whitespace
        text_parts = []
        for elem in root.iter():
            if elem.text and elem.text.strip():
                text_parts.append(elem.text.strip())
        return " ".join(text_parts)
