#!/usr/bin/env python3
"""Download the first Word attachment URL from a GitHub issue body or a supplied URL."""
from __future__ import annotations
import argparse
import os
import re
from pathlib import Path
from urllib.parse import unquote, urlparse
import requests

PATTERNS = [
    r"https://github\.com/user-attachments/(?:files|assets)/[^\s)<>\]]+",
    r"https://(?:objects\.githubusercontent\.com|github-production-user-asset-[^/]+\.s3\.amazonaws\.com)/[^\s)<>\]]+",
    r"https?://[^\s)<>\]]+\.docx(?:\?[^\s)<>\]]*)?",
]


def find_url(text: str) -> str:
    for pattern in PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0).rstrip(".,;\"")
    raise RuntimeError("No .docx or GitHub user-attachment URL found")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="")
    parser.add_argument("--body-file", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    body = args.body_file.read_text(encoding="utf-8") if args.body_file else ""
    url = args.url.strip() or find_url(body)
    headers = {"User-Agent": "XieLabMemberImporter/1.0"}
    token = os.getenv("GITHUB_TOKEN", "")
    if token and ("github.com" in url or "githubusercontent.com" in url):
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get(url, headers=headers, timeout=120, allow_redirects=True)
    response.raise_for_status()
    if len(response.content) > 25 * 1024 * 1024:
        raise RuntimeError("Downloaded file exceeds 25 MB")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(response.content)
    print(f"Downloaded {unquote(Path(urlparse(url).path).name)} to {args.out}")


if __name__ == "__main__":
    main()
