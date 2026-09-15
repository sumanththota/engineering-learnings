"""Pure ranking/filtering logic for search_learnings (spec 0002, issue #4).

Operates only on an already-parsed list of INDEX.json entries -- no
filesystem or network access here, mirroring reindex.py's separation of
pure build logic from IO. The MCP tool registered in server.py is a thin
adapter that reads INDEX.json and calls search_learnings() below.
"""

# Base score per field where the query substring-matches. id is the
# strongest signal (an agent typing an id wants that entry first),
# tags/project are secondary filters that still contribute to relevance.
ID_MATCH_SCORE = 3
TAG_MATCH_SCORE = 2
PROJECT_MATCH_SCORE = 1

# Corroboration boost is per-corroborating-link, so a well-corroborated
# Principle can outrank a merely-exact-matching but uncorroborated entry.
CORROBORATION_WEIGHT = 0.5

# A flat penalty for being superseded -- large enough to sink a superseded
# entry below its replacement in the common case, but the entry is never
# dropped from results.
SUPERSEDED_PENALTY = 5


def _text_score(entry: dict, query: str) -> float:
    query = query.lower()
    score = 0.0
    entry_id = (entry.get("id") or "").lower()
    if query == entry_id:
        score += ID_MATCH_SCORE * 2  # exact id match ranks above a mere substring hit
    elif query in entry_id:
        score += ID_MATCH_SCORE

    tags = [t.lower() for t in (entry.get("tags") or [])]
    if any(query == t for t in tags):
        score += TAG_MATCH_SCORE
    elif any(query in t for t in tags):
        score += TAG_MATCH_SCORE * 0.5

    project = (entry.get("project") or "").lower()
    if query == project:
        score += PROJECT_MATCH_SCORE
    elif query in project:
        score += PROJECT_MATCH_SCORE * 0.5

    return score


def search_learnings(entries, query=None, tags=None, project=None) -> list:
    """Rank and filter already-parsed INDEX.json entries.

    query: substring/exact match against id/tags/project, field-weighted.
    tags: entry must have at least one of these tags (unrecognized tags
        simply match nothing, per ADR 0009 -- no error).
    project: entry's project must exact-match.

    Every matching entry is returned, including superseded ones -- they're
    penalized in score, never filtered out (CONTEXT.md: Superseded).
    """
    tag_filter = set(tags) if tags else None
    results = []

    for entry in entries:
        if tag_filter is not None and not (tag_filter & set(entry.get("tags") or [])):
            continue
        if project is not None and entry.get("project") != project:
            continue

        score = 0.0
        if query:
            score = _text_score(entry, query)
            if score == 0.0:
                continue  # query given but nothing matched -- not a result

        score += (entry.get("corroboration") or 0) * CORROBORATION_WEIGHT
        if entry.get("superseded_by"):
            score -= SUPERSEDED_PENALTY

        results.append((score, entry))

    results.sort(key=lambda pair: pair[0], reverse=True)
    return [entry for _, entry in results]
