#!/usr/bin/env python3
"""Normalization, validation, deterministic matching and merge helpers for lab members."""
from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import datetime, timezone
from typing import Any

ALLOWED_GROUPS = {
    "principal-investigator", "faculty", "research-scientist", "postdoc",
    "phd", "master", "undergraduate", "staff", "visitor", "alumni"
}
ALLOWED_STATUS = {"current", "alumni", "inactive"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def list_of_text(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = re.split(r"[;；|\n]", value)
    if not isinstance(value, list):
        value = [value]
    out: list[str] = []
    for item in value:
        cleaned = text(item)
        if cleaned and cleaned not in out:
            out.append(cleaned)
    return out


def ascii_slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    return slug[:80]


def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").lower()
    return re.sub(r"[^\w\u4e00-\u9fff]+", "", value)


def normalize_member(raw: dict[str, Any], *, source_doc: str = "") -> dict[str, Any]:
    name_en = text(raw.get("name_en") or raw.get("english_name"))
    name_zh = text(raw.get("name_zh") or raw.get("chinese_name"))
    legacy_name = text(raw.get("name"))
    if legacy_name and not (name_en or name_zh):
        if re.search(r"[\u4e00-\u9fff]", legacy_name):
            parts = [p.strip() for p in re.split(r"\s*/\s*", legacy_name, maxsplit=1)]
            if len(parts) == 2:
                name_en, name_zh = parts[0], parts[1]
            else:
                name_zh = legacy_name
        else:
            name_en = legacy_name

    group = text(raw.get("group") or "staff").lower().replace("_", "-")
    if group not in ALLOWED_GROUPS:
        group = "staff"
    status = text(raw.get("status") or ("alumni" if group == "alumni" else "current")).lower()
    if status not in ALLOWED_STATUS:
        status = "current"
    if status == "alumni":
        group = "alumni"

    try:
        order = int(raw.get("order", 100))
    except (TypeError, ValueError):
        order = 100

    member_id = text(raw.get("id")) or ascii_slug(name_en) or ascii_slug(text(raw.get("email")).split("@")[0])
    if not member_id and name_zh:
        member_id = "member-" + hashlib.sha256(name_zh.encode("utf-8")).hexdigest()[:10]

    return {
        "id": member_id,
        "name_en": name_en,
        "name_zh": name_zh,
        "role_en": text(raw.get("role_en") or raw.get("role")),
        "role_zh": text(raw.get("role_zh")),
        "group": group,
        "status": status,
        "order": order,
        "bio_en": text(raw.get("bio_en") or raw.get("bio")),
        "bio_zh": text(raw.get("bio_zh")),
        "research_interests_en": list_of_text(raw.get("research_interests_en")),
        "research_interests_zh": list_of_text(raw.get("research_interests_zh")),
        "education_en": list_of_text(raw.get("education_en")),
        "education_zh": list_of_text(raw.get("education_zh")),
        "email": text(raw.get("email")).lower(),
        "orcid": text(raw.get("orcid")),
        "google_scholar": text(raw.get("google_scholar")),
        "homepage": text(raw.get("homepage")),
        "photo": text(raw.get("photo")),
        "joined": text(raw.get("joined")),
        "left": text(raw.get("left")),
        "source_doc": text(raw.get("source_doc") or source_doc),
        "updated_at": text(raw.get("updated_at")) or utc_now(),
    }


def validate_members(members: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    seen_emails: set[str] = set()
    for index, raw in enumerate(members):
        member = normalize_member(raw)
        label = member.get("name_en") or member.get("name_zh") or f"record {index + 1}"
        if not (member["name_en"] or member["name_zh"]):
            errors.append(f"{label}: name_en or name_zh is required")
        if not member["id"]:
            errors.append(f"{label}: id is required")
        elif member["id"] in seen_ids:
            errors.append(f"{label}: duplicate id {member['id']}")
        seen_ids.add(member["id"])
        if member["email"]:
            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", member["email"]):
                errors.append(f"{label}: invalid email {member['email']}")
            if member["email"] in seen_emails:
                errors.append(f"{label}: duplicate email {member['email']}")
            seen_emails.add(member["email"])
        if member["photo"] and not member["photo"].startswith(("assets/", "http://", "https://")):
            errors.append(f"{label}: photo must be an assets/ path or URL")
    return errors


def find_match(existing: list[dict[str, Any]], incoming: dict[str, Any]) -> int | None:
    incoming_email = text(incoming.get("email")).lower()
    incoming_id = text(incoming.get("id"))
    incoming_names = {normalize_name(text(incoming.get("name_en"))), normalize_name(text(incoming.get("name_zh")))} - {""}
    for idx, current in enumerate(existing):
        if incoming_email and incoming_email == text(current.get("email")).lower():
            return idx
        if incoming_id and incoming_id == text(current.get("id")):
            return idx
        current_names = {
            normalize_name(text(current.get("name_en"))),
            normalize_name(text(current.get("name_zh"))),
            normalize_name(text(current.get("name"))),
        } - {""}
        if incoming_names & current_names:
            return idx
    return None


def merge_member_records(existing_raw: list[dict[str, Any]], changes: list[dict[str, Any]], *, source_doc: str) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    existing = [normalize_member(item) for item in existing_raw]
    audit: list[dict[str, str]] = []
    for change in changes:
        action = text(change.get("action") or "upsert").lower()
        candidate_raw = change.get("member") if isinstance(change.get("member"), dict) else change
        candidate = normalize_member(candidate_raw, source_doc=source_doc)
        idx = find_match(existing, candidate)
        label = candidate.get("name_en") or candidate.get("name_zh") or candidate.get("id")

        if action in {"archive", "alumni", "deactivate"}:
            if idx is None:
                candidate["status"] = "alumni"
                candidate["group"] = "alumni"
                existing.append(candidate)
                audit.append({"action": "add-as-alumni", "member": label})
            else:
                existing[idx]["status"] = "alumni"
                existing[idx]["group"] = "alumni"
                existing[idx]["left"] = candidate.get("left") or existing[idx].get("left", "")
                existing[idx]["updated_at"] = utc_now()
                existing[idx]["source_doc"] = source_doc
                audit.append({"action": "archive", "member": label})
            continue

        if action == "delete":
            if idx is not None:
                removed = existing.pop(idx)
                audit.append({"action": "delete", "member": removed.get("name_en") or removed.get("name_zh") or label})
            else:
                audit.append({"action": "delete-not-found", "member": label})
            continue

        if idx is None:
            existing.append(candidate)
            audit.append({"action": "add", "member": label})
        else:
            merged = dict(existing[idx])
            for key, value in candidate.items():
                if value not in ("", [], None):
                    merged[key] = value
            merged["updated_at"] = utc_now()
            merged["source_doc"] = source_doc
            existing[idx] = normalize_member(merged)
            audit.append({"action": "update", "member": label})

    existing.sort(key=lambda item: (1 if item.get("status") == "alumni" else 0, int(item.get("order", 100)), text(item.get("name_en") or item.get("name_zh")).lower()))
    return existing, audit
