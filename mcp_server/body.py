"""IO seam that attaches each search result's full body content (spec 0002
follow-up): search_learnings alone returns metadata only, which requires a
caller to separately Read the file to get the actual Why/How-to-apply text --
a second step that's easy to skip, silently leaving an agent reasoning from
an id/tags guess instead of the real content. attach_bodies() closes that gap
by reading every result's file inline, so a search result is self-contained.

Deliberately its own module rather than added to search.py: search.py's
ranking stays filesystem-free (spec 0002's tested seam), while this is pure
IO, mirroring writer.py's precedent of a dedicated module for the IO-side
concern.
"""
import sys
import warnings
from pathlib import Path

# scripts/ has no __init__.py; mirrors writer.py's sys.path setup so it's
# importable as a package once the repo root is on sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.reindex import read_body  # noqa: E402


def attach_bodies(results: list[dict], repo_path) -> list[dict]:
    """Return a new list of result dicts, each with a `body` field read from
    its `file` path (relative to repo_path). Does not mutate the input.

    A result whose file is missing or has no readable frontmatter (INDEX.json
    stale relative to the working tree) is dropped with a warning rather than
    raising -- one bad entry shouldn't crash every other result in the call,
    matching this repo's warn-not-fail posture elsewhere (ADR 0009).
    """
    repo_path = Path(repo_path)
    attached = []
    for result in results:
        path = repo_path / result["file"]
        try:
            text = path.read_text()
            body = read_body(text)
        except (FileNotFoundError, ValueError) as e:
            warnings.warn(f"{result['file']}: skipping body attach -- {e}", stacklevel=2)
            continue
        attached.append({**result, "body": body})
    return attached
