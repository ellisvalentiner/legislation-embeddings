#!/usr/bin/env python3
# ~*~ coding: utf-8 ~*~
"""Scrapy spider for scraping Congress data."""

import json
import os
from datetime import datetime
from urllib.parse import urlparse

import scrapy
from scrapy.http import Response


class LegislationSpider(scrapy.Spider):
    """Scrapy spider for scraping Congress data."""

    name = "legislation"
    start_urls = [
        f"https://www.govinfo.gov/bulkdata/json/BILLS/{congress}"
        for congress in range(113, 119)
    ]

    def __init__(
        self, output_dir="data", state_file="download_state.json", *args, **kwargs
    ):
        super(LegislationSpider, self).__init__(*args, **kwargs)
        self.output_dir = output_dir
        self.state_file = state_file
        os.makedirs(output_dir, exist_ok=True)
        self.downloaded_files = self._load_state()

    def _load_state(self):
        """Load the state of previously downloaded files."""
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                return json.load(f)
        return {}

    def _save_state(self):
        """Save the state of downloaded files."""
        with open(self.state_file, "w") as f:
            json.dump(self.downloaded_files, f)

    def closed(self, reason):
        """Save state when spider closes."""
        self._save_state()

    def start_requests(self):
        """Yield the initial requests."""
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: Response, **kwargs):
        """Parse the response and yield the next request."""
        content_type_bytes = response.headers.get("Content-Type", def_val=b"")
        if content_type_bytes is None:
            content_type_bytes = b""
        content_type = content_type_bytes.decode()

        if "application/json" in content_type:
            body = json.loads(response.body.decode())
            files = body.get("files", [])
            for file in files:
                url = file["link"]
                # Check if we need to download this file
                if not self._should_download(url, file):
                    self.logger.info(f"Skipping already downloaded file: {url}")
                    continue

                yield response.follow(
                    url, callback=self.parse, meta={"file_info": file}
                )
        elif "text/xml" in content_type or "application/xml" in content_type:
            url = response.url
            filename = os.path.basename(urlparse(url).path)
            filepath = os.path.join(self.output_dir, filename)

            # Save the file
            with open(filepath, "wb") as f:
                f.write(response.body)

            last_modified_bytes = response.headers.get("Last-Modified", def_val=b"")
            if last_modified_bytes is None:
                last_modified_bytes = b""

            # Update state
            self.downloaded_files[url] = {
                "filename": filename,
                "filepath": filepath,
                "last_modified": last_modified_bytes.decode(),
                "download_date": datetime.now().isoformat(),
                "size": len(response.body),
            }

            yield {"url": url, "file": filepath, "status": "downloaded"}

    def _should_download(self, url, file_info):
        """
        Determine if we should download a file based on:
        1. Whether we've downloaded it before
        2. If the file has been modified since our last download
        """
        if url not in self.downloaded_files:
            return True

        # If the file has a lastModified field, compare it
        if "lastModified" in file_info:
            previous_modified = self.downloaded_files[url].get("last_modified")
            if previous_modified != file_info["lastModified"]:
                return True

        return False
