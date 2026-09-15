#!/usr/bin/env python3
"""Rebuild INDEX.json from learnings/*.md frontmatter, validating links and
computing corroboration from the link graph. No deps beyond stdlib."""
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEARNINGS_DIR = REPO_ROOT / "learnings"
INDEX_PATH = REPO_ROOT / "INDEX.json"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

# Canonical tag vocabulary (CONTEXT.md, ADR 0009). A tag outside this list
# warns rather than fails, so vocabulary growth is deliberate, not silent.
CANONICAL_TAGS = {
    "agents", "debugging", "dependencies", "efficiency", "fixtures", "git",
    "interfaces", "orchestration", "parallelism", "planning", "principle",
    "process", "provenance", "reproducibility", "review", "testing",
    "verification",
}

REQUIRED_FIELDS = ["id", "date", "project", "tags", "type", "links"]


class DanglingLinkError(ValueError):
    def __init__(self, file_name, dangling_id, warnings=None):
        self.file_name = file_name
        self.dangling_id = dangling_id
        self.warnings = warnings or []
        super().__init__(f"{file_name}: links to unknown id '{dangling_id}'")


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


def parse_learnings(learnings_dir: Path):
    """Parse every learnings/*.md file's frontmatter.

    Returns (parsed, warnings) where parsed is a list of (path, fields) and
    warnings flags any file missing a required field.
    """
    parsed = []
    warnings = []
    for path in sorted(learnings_dir.glob("*.md")):
        fields = parse_frontmatter(path.read_text())
        missing = [f for f in REQUIRED_FIELDS if f not in fields]
        if missing:
            warnings.append(f"{path.name} missing fields {missing}")
        parsed.append((path, fields))
    return parsed, warnings


def validate_links(parsed, warnings=None):
    """Raise DanglingLinkError if any entry's links reference an id absent
    from this corpus. `warnings` (e.g. missing-field warnings already
    collected) is attached to the exception so a caller doesn't lose them."""
    ids = {fields.get("id", path.stem) for path, fields in parsed}
    for path, fields in parsed:
        for linked_id in fields.get("links") or []:
            if linked_id not in ids:
                raise DanglingLinkError(path.name, linked_id, warnings=warnings)


def check_tags(parsed):
    """Return a warning for every tag outside CANONICAL_TAGS. Never fails."""
    warnings = []
    for path, fields in parsed:
        for tag in fields.get("tags") or []:
            if tag not in CANONICAL_TAGS:
                warnings.append(f"{path.name} uses unrecognized tag '{tag}'")
    return warnings


def compute_corroboration(parsed):
    """Map each id to the count of *other* entries whose links reference it
    (a self-link never corroborates itself)."""
    counts = {fields.get("id", path.stem): 0 for path, fields in parsed}
    for path, fields in parsed:
        entry_id = fields.get("id", path.stem)
        for linked_id in fields.get("links") or []:
            if linked_id in counts and linked_id != entry_id:
                counts[linked_id] += 1
    return counts


def build_index(learnings_dir: Path):
    """Pure build: parse, validate, and shape every entry for INDEX.json.

    Returns (entries, warnings). Raises DanglingLinkError on a links id that
    doesn't resolve within this corpus.
    """
    parsed, missing_field_warnings = parse_learnings(learnings_dir)
    validate_links(parsed, warnings=missing_field_warnings)
    tag_warnings = check_tags(parsed)
    corroboration = compute_corroboration(parsed)

    entries = []
    for path, fields in parsed:
        entry_id = fields.get("id", path.stem)
        entries.append({
            "id": entry_id,
            "file": f"learnings/{path.name}",
            "date": fields.get("date"),
            "project": fields.get("project"),
            "tags": fields.get("tags") or [],
            "type": fields.get("type"),
            "links": fields.get("links") or [],
            "corroboration": corroboration.get(entry_id, 0),
            "superseded_by": fields.get("superseded_by"),
            "embedding": None,
        })
    return entries, missing_field_warnings + tag_warnings


def main():
    try:
        entries, warnings = build_index(LEARNINGS_DIR)
    except DanglingLinkError as e:
        for warning in e.warnings:
            print(f"warning: {warning}", file=sys.stderr)
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)

    INDEX_PATH.write_text(json.dumps(entries, indent=2) + "\n")
    print(f"wrote {len(entries)} entries to {INDEX_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
