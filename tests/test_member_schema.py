from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from member_schema import merge_member_records, normalize_member, validate_members  # noqa: E402


class MemberSchemaTests(unittest.TestCase):
    def test_normalize_member(self) -> None:
        member = normalize_member({"name_en": " Jane   Doe ", "group": "phd", "email": "JANE@EXAMPLE.ORG"})
        self.assertEqual(member["name_en"], "Jane Doe")
        self.assertEqual(member["email"], "jane@example.org")
        self.assertEqual(member["status"], "current")

    def test_merge_matches_email_and_preserves_blank_fields(self) -> None:
        existing = [{"id": "jane-doe", "name_en": "Jane Doe", "bio_en": "Existing", "email": "jane@example.org"}]
        changes = [{"action": "upsert", "member": {"name_en": "Jane D.", "email": "jane@example.org", "role_en": "Postdoctoral Researcher", "bio_en": ""}}]
        merged, audit = merge_member_records(existing, changes, source_doc="update.docx")
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["bio_en"], "Existing")
        self.assertEqual(merged[0]["role_en"], "Postdoctoral Researcher")
        self.assertEqual(audit[0]["action"], "update")

    def test_archive_is_explicit(self) -> None:
        existing = [{"id": "jane-doe", "name_en": "Jane Doe", "group": "phd", "status": "current"}]
        changes = [{"action": "archive", "member": {"id": "jane-doe", "name_en": "Jane Doe", "left": "2026"}}]
        merged, _ = merge_member_records(existing, changes, source_doc="update.docx")
        self.assertEqual(merged[0]["status"], "alumni")
        self.assertEqual(merged[0]["group"], "alumni")

    def test_validation_rejects_duplicate_email(self) -> None:
        errors = validate_members([
            {"id": "a", "name_en": "A", "email": "same@example.org"},
            {"id": "b", "name_en": "B", "email": "same@example.org"},
        ])
        self.assertTrue(any("duplicate email" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
