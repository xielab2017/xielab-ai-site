from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("import_cms_issue", ROOT / "scripts" / "import_cms_issue.py")
assert SPEC and SPEC.loader
cms = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cms)


class CmsIssueTests(unittest.TestCase):
    def test_parse_console_payload(self) -> None:
        text = """Collection: research
Operation: upsert
Key: id:microbiome
AI assist: false

```json
{"id":"microbiome","title_en":"Microbiome","title_zh":"微生物组"}
```
Editorial note:
Test.
Review all factual information.
"""
        parsed = cms.parse_issue(text)
        self.assertEqual(parsed["collection"], "research")
        self.assertEqual(parsed["operation"], "upsert")
        self.assertFalse(parsed["ai_assist"])
        self.assertEqual(parsed["record"]["id"], "microbiome")

    def test_parse_github_issue_form(self) -> None:
        text = """### Collection

site

### Operation

merge-object

### Stable key

name:Xie Lab

### AI assist

false

### JSON record

```json
{"name":"Xie Lab","email":"lab@example.org"}
```
"""
        parsed = cms.parse_issue(text)
        self.assertEqual(parsed["collection"], "site")
        self.assertEqual(parsed["key"], "name:Xie Lab")

    def test_list_upsert_and_delete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            (data_dir / "research.json").write_text(
                json.dumps([{"id": "existing", "title_en": "Existing", "title_zh": "已有"}]),
                encoding="utf-8",
            )
            previous = cms.DATA_DIR
            cms.DATA_DIR = data_dir
            try:
                parsed = {
                    "collection": "research", "operation": "upsert", "key": "id:new-direction",
                    "ai_assist": False, "record": {
                        "id": "new-direction", "title_en": "New", "title_zh": "新方向",
                        "text_en": "Text", "text_zh": "文字", "order": 2,
                    },
                }
                result = cms.apply_update(parsed, "unused")
                self.assertEqual(result["action"], "added")
                self.assertEqual(len(json.loads((data_dir / "research.json").read_text())), 2)
                parsed["operation"] = "delete"
                parsed["record"] = {"id": "new-direction"}
                result = cms.apply_update(parsed, "unused")
                self.assertEqual(result["action"], "deleted")
                self.assertEqual(len(json.loads((data_dir / "research.json").read_text())), 1)
            finally:
                cms.DATA_DIR = previous

    def test_object_merge_preserves_unsubmitted_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            (data_dir / "site.json").write_text(
                json.dumps({"name": "Xie Lab", "email": "old@example.org", "intro_en": "Keep me"}),
                encoding="utf-8",
            )
            previous = cms.DATA_DIR
            cms.DATA_DIR = data_dir
            try:
                parsed = {
                    "collection": "site", "operation": "merge-object", "key": "name:Xie Lab",
                    "ai_assist": False, "record": {"email": "new@example.org"},
                }
                cms.apply_update(parsed, "unused")
                result = json.loads((data_dir / "site.json").read_text())
                self.assertEqual(result["email"], "new@example.org")
                self.assertEqual(result["intro_en"], "Keep me")
            finally:
                cms.DATA_DIR = previous


if __name__ == "__main__":
    unittest.main()
