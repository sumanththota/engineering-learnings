# Spec: MCP retrieval/write server (search_learnings, add_learning)

## Problem Statement

Today, retrieving a Learning means an agent reads `INDEX.json` directly and filters it in-context (per ADR 0008) — there's no callable interface for search, so every session that wants to query the vault re-implements that filtering by hand. Adding a new Learning is worse: an agent or Sumanth has to hand-author a markdown file with the exact frontmatter shape from memory, with no validation that an `id` doesn't collide or a `links` entry doesn't dangle until the next `reindex.py` run. There's no single, reliable interface a Claude session can call to retrieve from or append to this vault.

## Solution

Build the small, purpose-built MCP server ADR 0008 already decided on, exposing exactly two tools: `search_learnings` and `add_learning`. It wraps `INDEX.json` directly rather than adopting a generic vault-search MCP server, because this repo has a small, specific domain model — Specific vs Principle, Corroboration derived from `links`, Superseded deprioritization — that a generic tool has no concept of. The server's core logic lives as two pure functions, one for ranking/filtering and one for writing a new Learning file; the MCP stdio transport is a thin wrapper around them, mirroring the precedent already set by `reindex.py`'s `build_index()` (ADR 0007, spec 0001): keep the tested seam separate from the process boundary.

## User Stories

1. As an AI agent in any session, I want to call `search_learnings(query, tags, project)`, so that I can retrieve relevant Learnings without reading and filtering `INDEX.json` by hand.
2. As an AI agent, I want search results ranked with Corroboration as a positive boost, so a well-corroborated Principle surfaces above a one-off Specific.
3. As an AI agent, I want a Superseded Learning penalized in ranking rather than hidden, so I still see it but prefer its replacement when one is at least as relevant.
4. As an AI agent, I want to filter search by `tags` drawn from the canonical vocabulary in `CONTEXT.md`, so I can narrow results to a relevant category.
5. As an AI agent, I want to filter search by `project`, so I can find Learnings from a specific context when that's what I need.
6. As an AI agent, I want exact/substring match on `id`, so I can fetch one entry directly when I already know its identity.
7. As Sumanth, I want `add_learning` invoked only when I explicitly ask for it in a session, so the vault's growth stays deliberate (ADR 0005) — no agent decides on its own that something is "worth capturing."
8. As Sumanth, I want `add_learning` to write a single new `learnings/*.md` file with correct frontmatter (`id`, `date`, `project`, `tags`, `type`, `links` — no `confidence` field, per ADR 0002), so a new Learning matches this repo's schema without me hand-typing YAML.
9. As Sumanth, I want `add_learning` to derive `id` from the given slug and treat it as frozen from creation (ADR 0003), so ids stay stable and grep-able.
10. As Sumanth, I want `add_learning` to refuse to write when a file with that `id` already exists, so a colliding id fails loudly instead of silently overwriting an existing Learning (ADR 0003's "never rename" implies never silently overwrite either).
11. As Sumanth, I want `add_learning` to reject a `links` entry that doesn't resolve to a real `id` in the current corpus, the same way `reindex.py`'s link validation will (spec 0001), so a typo doesn't sit invisibly broken until the next commit.
12. As Sumanth, I want `add_learning` to leave the new file uncommitted, so the existing manual-redaction review step (ADR 0006) stays the last gate before anything reaches git history.
13. As Sumanth, I want `add_learning` to not invoke `scripts/reindex.py` itself, so `INDEX.json` regeneration stays owned by the pre-commit hook (ADR 0007, spec 0001) instead of being duplicated in two places.
14. As Sumanth, I want `search_learnings` to read the already-committed `INDEX.json` rather than re-scanning `learnings/*.md`, so retrieval stays fast and parsing logic doesn't get duplicated outside `reindex.py`.
15. As Sumanth, I want the server to run with no configuration beyond pointing it at this repo's path, so I can attach it to any Claude session without per-project setup.
16. As an AI agent, I want an unrecognized tag passed to `search_learnings` to simply return zero matches rather than error, matching `reindex.py`'s warn-not-fail posture on the tag vocabulary (ADR 0009).
17. As Sumanth, I want `add_learning` to accept `type: specific` or `type: principle` and require the same fields either way, so the server doesn't special-case one kind over the other (matching spec 0001's uniform-treatment decision).
18. As an AI agent, I want `search_learnings` to return each result's `file` path alongside its metadata, so I can `Read` the full body when a summary isn't enough.
19. As Sumanth, I want the ranking logic to be pure and unit-testable against fixture data, not dependent on a live filesystem or a running MCP process, so it can be verified in isolation.
20. As Sumanth, I want the server to make no calls to any embedding provider or external network service, so search stays instant and free — the `embedding: null` field stays reserved but inactive (ADR 0001, original consolidation plan), not activated by this spec.

## Implementation Decisions

- **Search module**: a pure `search_learnings(entries, query=None, tags=None, project=None) -> list[dict]`, operating on the already-parsed list of `INDEX.json` entries (not re-reading files from disk). Ranking is a field-weighted linear scan (ADR 0008): exact/substring match on `id`/`tags`/`project` contributes to a base score; `corroboration` adds a positive boost; presence of `superseded_by` applies a penalty. No embeddings, no external ranking library.
- **Write module**: a pure-ish `add_learning(learnings_dir, id, date, project, tags, type, links, body) -> Path`. It: treats `id` as the frozen filename stem (ADR 0003); refuses to write if a file with that `id` already exists; validates every `links` entry resolves against the current corpus using the same logic `reindex.py`'s `validate_links` will use (spec 0001); writes frontmatter + body in the exact shape `reindex.py` already parses; returns the path written. It never calls `reindex.py` and never touches git.
- **Transport**: an MCP server process (stdio) that registers `search_learnings` and `add_learning` as MCP tools, marshalling tool-call arguments into the two functions above and their return values back into the MCP response shape. The transport module holds no ranking or writing logic of its own — it is a pure adapter.
- **Runtime/SDK**: Python, using the official `mcp` SDK for server/tool-registration boilerplate. Spec 0001's zero-dependency constraint is scoped to `reindex.py`'s commit-time build specifically; it doesn't extend to this server, so one runtime dependency here is acceptable.
- **Result schema**: `search_learnings` results carry the same fields as an `INDEX.json` entry (`id`, `file`, `date`, `project`, `tags`, `type`, `links`, `corroboration`, `superseded_by`, `embedding`) — enough for a caller to decide whether to `Read` the full file.
- **Required inputs**: `add_learning`'s required fields mirror `reindex.py`'s `REQUIRED_FIELDS` minus `confidence` (ADR 0002, once spec 0001 lands), plus a free-text `body`.
- **Unrecognized tags**: on either tool, warn-equivalent, not a hard failure — `search_learnings` with an unknown tag returns zero matches (not an error); `add_learning` with an unknown tag succeeds (ADR 0009: warn, don't block).

## Testing Decisions

- Primary seam: `search_learnings(entries, ...)` and `add_learning(learnings_dir, ...)` as pure/near-pure functions, tested directly against fixture data, with no MCP process or stdio transport involved — mirrors spec 0001's fixture-based testing of `build_index(learnings_dir)`.
- `search_learnings` fixtures should cover: exact id match, substring match, a tag filter, a project filter, corroboration boosting one entry above another, and a `superseded_by` entry ranking below its replacement.
- `add_learning` fixtures should cover: a valid write, a collision on an existing `id` (must fail, must not overwrite), a dangling `links` id (must fail), and a round-trip — write a file, then confirm `reindex.py`'s own parser reads it back with matching fields.
- No MCP-transport-level automated tests planned initially — a manual integration check (attach the server to a session, call each tool once) is the equivalent of spec 0001's manual pre-commit-hook check.
- Use stdlib `unittest`, consistent with spec 0001's choice for the rest of this repo.

## Out of Scope

- Everything spec 0001 delivers (corroboration computation, link validation, `.githooks/pre-commit`) — this spec depends on spec 0001 landing first. `search_learnings`'s corroboration boost and `add_learning`'s link validation both assume spec 0001's `INDEX.json` shape and `validate_links` logic already exist.
- Embeddings-based or semantic search — `embedding: null` stays reserved and unused (ADR 0001, original consolidation plan); this spec is field-weighted scan only.
- Automated redaction or secret scanning on `add_learning` — manual review stays the only gate (ADR 0006).
- Proactive or autonomous lesson capture — `add_learning` is only ever called because Sumanth explicitly asked in-session (ADR 0005); nothing here makes the server decide on its own to add something.
- Editing an existing Learning or marking one `superseded_by` via the server (ADR 0004) — `add_learning` only creates new files; superseding stays a manual edit for now.
- Running `reindex.py`, or committing/pushing, on `add_learning`'s behalf.
- Any UI, dashboard, or table beyond the two MCP tools themselves.

## Further Notes

This formalizes ADR 0008's decision into a buildable plan. It's stage 5 of the pipeline sketched in spec 0001's Further Notes (author → commit-time build → repo → retrieval today → **future MCP server** → agent harness), sequenced after spec 0001 (stage 2) because `search_learnings`'s corroboration boost and `add_learning`'s link validation both need spec 0001's `INDEX.json` shape and validation logic to exist first. `/to-tickets` should encode this as a blocking edge between the two specs' ticket sets rather than let this spec's tickets start immediately.
