#!/usr/bin/env python3
"""Validate all public structured-content collections before deployment."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from member_schema import validate_members  # noqa: E402

COLLECTIONS = ["research", "members", "tools", "publications", "patents", "news"]


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path.relative_to(ROOT)}: {exc}") from exc


def is_url(value: str) -> bool:
    return not value or bool(re.match(r"^https?://", value))


def validate_unique(records: list[dict[str, Any]], fields: tuple[str, ...], label: str) -> list[str]:
    errors: list[str] = []
    seen: dict[tuple[str, str], int] = {}
    for index, record in enumerate(records, start=1):
        for field in fields:
            value = str(record.get(field) or "").strip().lower()
            if not value:
                continue
            key = (field, value)
            if key in seen:
                errors.append(f"{label}: duplicate {field} in records {seen[key]} and {index}: {value}")
            else:
                seen[key] = index
    return errors


def validate() -> list[str]:
    errors: list[str] = []
    site = load_json(ROOT / "data" / "site.json")
    if not isinstance(site, dict):
        errors.append("data/site.json must be a JSON object")
    for key in ("name", "tagline_en", "tagline_zh", "email"):
        if not str(site.get(key) or "").strip():
            errors.append(f"data/site.json: missing {key}")

    for key in ("github", "google_scholar", "pubmed", "legacy_source"):
        value = str(site.get(key) or "").strip()
        if value and not is_url(value):
            errors.append(f"data/site.json: invalid URL in {key}")

    openings = load_json(ROOT / "data" / "openings.json")
    if not isinstance(openings, dict):
        errors.append("data/openings.json must be a JSON object")
    else:
        for key in ("en", "zh"):
            if not str(openings.get(key) or "").strip():
                errors.append(f"data/openings.json: missing {key}")

    data: dict[str, list[dict[str, Any]]] = {}
    for name in COLLECTIONS:
        value = load_json(ROOT / "data" / f"{name}.json")
        if not isinstance(value, list):
            errors.append(f"data/{name}.json must be a JSON array")
            continue
        if any(not isinstance(item, dict) for item in value):
            errors.append(f"data/{name}.json must contain objects only")
            continue
        data[name] = value

    if "members" in data:
        errors.extend(f"members: {error}" for error in validate_members(data["members"]))
    if "publications" in data:
        errors.extend(validate_unique(data["publications"], ("doi", "pmid"), "publications"))
        for index, item in enumerate(data["publications"], start=1):
            if not str(item.get("title") or "").strip():
                errors.append(f"publications: record {index} has no title")
    if "patents" in data:
        errors.extend(validate_unique(data["patents"], ("publication_number", "url"), "patents"))
        for index, item in enumerate(data["patents"], start=1):
            if item.get("url") and not is_url(str(item["url"])):
                errors.append(f"patents: record {index} has an invalid URL")
    if "tools" in data:
        errors.extend(validate_unique(data["tools"], ("id", "url", "name"), "tools"))
        for index, item in enumerate(data["tools"], start=1):
            if item.get("url") and not is_url(str(item["url"])):
                errors.append(f"tools: record {index} has an invalid URL")
            if not str(item.get("name") or "").strip():
                errors.append(f"tools: record {index} has no name")
    if "research" in data:
        errors.extend(validate_unique(data["research"], ("id",), "research"))
        for index, item in enumerate(data["research"], start=1):
            if not str(item.get("title_en") or item.get("title_zh") or "").strip():
                errors.append(f"research: record {index} has no title")
    if "news" in data:
        errors.extend(validate_unique(data["news"], ("id",), "news"))
        for index, item in enumerate(data["news"], start=1):
            if not str(item.get("title_en") or item.get("title_zh") or "").strip():
                errors.append(f"news: record {index} has no title")

    return errors


def main() -> None:
    errors = validate()
    if errors:
        print("Content validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    counts = []
    for name in COLLECTIONS:
        value = load_json(ROOT / "data" / f"{name}.json")
        counts.append(f"{name}={len(value)}")
    print("Content validation passed: " + ", ".join(counts))


if __name__ == "__main__":
    main()
