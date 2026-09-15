#!/usr/bin/env python3
"""Rebuild INDEX.json from learnings/*.md frontmatter. No deps beyond stdlib."""
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEARNINGS_DIR = REPO_ROOT / "learnings"
INDEX_PATH = REPO_ROOT / "INDEX.json"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_scalar(value: str):
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [v.strip().strip('"').strip("'") for v in inner.split(",")]
    if value.lower() == "null":
        return None
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> dict:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("missing frontmatter block")
    fields = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = parse_scalar(value)
    return fields

REQUIRED_FIELDS = ["id", "date", "project", "tags", "type", "confidence", "links"]


def build_index():
    entries = []
    for path in sorted(LEARNINGS_DIR.glob("*.md")):
        text = path.read_text()
        fields = parse_frontmatter(text)
        missing = [f for f in REQUIRED_FIELDS if f not in fields]
        if missing:
            print(f"warning: {path.name} missing fields {missing}", file=sys.stderr)
        entries.append({
            "id": fields.get("id", path.stem),
            "file": f"learnings/{path.name}",
            "date": fields.get("date"),
            "project": fields.get("project"),
            "tags": fields.get("tags") or [],
            "type": fields.get("type"),
            "confidence": fields.get("confidence"),
            "links": fields.get("links") or [],
            "embedding": None,
        })
    INDEX_PATH.write_text(json.dumps(entries, indent=2) + "\n")
    print(f"wrote {len(entries)} entries to {INDEX_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    build_index()
