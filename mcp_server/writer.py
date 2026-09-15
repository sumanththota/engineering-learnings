"""Pure-ish write module for the engineering-learnings vault (spec 0002).

add_learning() writes one new learnings/*.md file in the exact frontmatter
shape scripts/reindex.py already parses. It reuses reindex.py's own
validate_links() (rather than re-implementing link-integrity rules) so the
two never diverge, and it never calls reindex.py or touches git -- the new
file is left uncommitted for the manual review step (ADR 0006) and the next
pre-commit reindex (ADR 0007).
"""
import sys
import warnings
from pathlib import Path

# scripts/ has no __init__.py; it's a namespace package importable once the
# repo root is on sys.path (mirrors tests/test_reindex.py's sys.path insert,
# adapted to package-import form since this module isn't a top-level script).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.reindex import (  # noqa: E402
    check_tags,
    parse_learnings,
    validate_links,
)

REQUIRED_FIELDS = ["id", "date", "project", "tags", "type", "links"]  # mirrors reindex.py, minus confidence (ADR 0002)
VALID_TYPES = {"specific", "principle"}


def _format_frontmatter(id, date, project, tags, type, links) -> str:
    """Render frontmatter in the exact shape reindex.py's parse_frontmatter expects.

    No `confidence` field is ever emitted (ADR 0002), even though some
    pre-existing files still carry a stray one from before that ADR landed.
    """
    lines = [
        "---",
        f"id: {id}",
        f"date: {date}",
        f"project: {project}",
        f"tags: [{', '.join(tags)}]",
        f"type: {type}",
        f"links: [{', '.join(links)}]",
        "---",
    ]
    return "\n".join(lines)


def add_learning(learnings_dir, id, date, project, tags, type, links, body) -> Path:
    """Write learnings_dir/<id>.md and return its Path.

    Required fields mirror reindex.py's REQUIRED_FIELDS minus `confidence`
    (ADR 0002), plus `body`. Fails loudly (raises) rather than writing
    anything, in three cases:
      - `id` is not a safe filename stem (path separators, empty, "." / "..")
      - a file with that `id` already exists (ADR 0003: never overwrite)
      - `type` isn't "specific" or "principle"
      - any `links` entry doesn't resolve to a real id in the current corpus,
        checked with reindex.py's own validate_links()

    An unrecognized tag (outside CONTEXT.md's canonical vocabulary) warns via
    the stdlib `warnings` module rather than failing (ADR 0009).
    """
    learnings_dir = Path(learnings_dir)
    tags = list(tags or [])
    links = list(links or [])

    if not id or "/" in id or "\\" in id or id in (".", ".."):
        raise ValueError(f"invalid id {id!r}: must be a plain filename stem")
    if type not in VALID_TYPES:
        raise ValueError(f"invalid type {type!r}: must be one of {sorted(VALID_TYPES)}")

    dest = learnings_dir / f"{id}.md"
    if dest.exists():
        raise FileExistsError(f"a learning with id '{id}' already exists at {dest} -- ids are frozen (ADR 0003), refusing to overwrite")

    # Validate links against the existing corpus plus this not-yet-written
    # entry, via reindex.py's own validate_links so the rule can't diverge.
    parsed, _ = parse_learnings(learnings_dir)
    candidate_entry = (dest, {"id": id, "links": links})
    validate_links(parsed + [candidate_entry])  # raises DanglingLinkError on a dangling id

    for warning in check_tags([(dest, {"tags": tags})]):
        warnings.warn(warning, stacklevel=2)

    dest.write_text(_format_frontmatter(id, date, project, tags, type, links) + "\n\n" + body.rstrip("\n") + "\n")
    return dest
