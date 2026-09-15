# Spec: Reindex build pipeline (validation, corroboration, pre-commit hook)

## Problem Statement

`INDEX.json` is only regenerated when `scripts/reindex.py` is run by hand, so it can silently drift from `learnings/*.md`. Nothing today catches a `links` entry pointing at an id that doesn't exist — it just quietly loses an edge in the corroboration graph. Tags can drift into synonyms with no enforcement, splitting one search facet into two. The old `confidence` field was hand-typed and has already been decided against (ADR 0002) in favor of a computed `corroboration`, but nothing computes it yet. None of this is caught until a human happens to notice — which defeats the point of `INDEX.json` being the retrieval surface an agent is meant to trust.

## Solution

Rewrite `scripts/reindex.py` so it validates the corpus while it builds the index: every Learning's `links` must resolve to a real id or the build fails; an unrecognized tag produces a warning, not a failure; every entry's `corroboration` is computed from the link graph instead of authored by hand; `superseded_by` is passed through when a file has one. Wire this into a tracked git pre-commit hook so `INDEX.json` can never be committed stale or inconsistent with the Learnings it's built from.

## User Stories

1. As Sumanth, I want the build to fail loudly when a `links` id doesn't resolve, so that a typo or a stale reference to a renamed file can't silently undercount corroboration.
2. As Sumanth, I want an unrecognized tag to produce a warning rather than block my commit, so that the vocabulary can grow deliberately without friction.
3. As Sumanth, I want `corroboration` computed from the link graph, so that I never have to remember to hand-update a count on a Principle when a new Specific links to it.
4. As Sumanth, I want `superseded_by` passed through into `INDEX.json` when a file has it, so that a Superseded Learning's replacement is visible to anything reading the index, not just to someone opening the file.
5. As Sumanth, I want a pre-commit hook that runs the build and re-stages `INDEX.json` automatically, so that I can never commit a Learning file without the index reflecting it.
6. As Sumanth, I want the hook to block the commit when the build fails (e.g. a dangling link), so that a broken corpus never reaches git history.
7. As Sumanth, I want the hook to live in a tracked path (not raw `.git/hooks/`), so that cloning this repo elsewhere doesn't silently lose the safety net.
8. As Sumanth, I want the existing required-field warnings (missing `id`, `date`, etc.) preserved, so that this rewrite doesn't regress checks that already work.
9. As Sumanth, I want `embedding: null` left untouched by this change, so that the reserved seam for a future MCP server (ADR 0001) isn't disturbed.
10. As Sumanth, I want `type: specific` and `type: principle` entries treated identically by the build (no special-casing), so that corroboration and link-validation logic stays uniform regardless of a Learning's kind.
11. As an AI agent reading `INDEX.json`, I want `corroboration` to be a trustworthy, freshly-computed number, so that I can rank a well-corroborated Principle above a one-off Specific without separately verifying the link graph myself.
12. As Sumanth, I want the build to keep working with zero dependencies beyond the Python standard library, so that the repo doesn't need a package manager just to stay indexed.

## Implementation Decisions

- **Module touched:** `scripts/reindex.py` — decomposed into small, pure functions rather than one monolithic `build_index()`: a parse step (unchanged — reads frontmatter per file), a `validate_links` step (every `links` id must exist in the set of parsed ids; raises/exits non-zero on failure, naming the offending file and id), a `check_tags` step (compares each file's `tags` against a canonical constant list; emits a warning to stderr per unrecognized tag, does not fail), and a `compute_corroboration` step (for each entry, counts how many other entries' `links` arrays contain its id).
- **Schema change:** `confidence` is removed from `REQUIRED_FIELDS` and from the output entry shape entirely (ADR 0002). `corroboration` (integer) is added to every output entry, always computed, never read from frontmatter. `superseded_by` becomes an optional passthrough field (string id or `null`), not required.
- **Canonical tag list:** the 16 tags currently listed in `CONTEXT.md` (agents, debugging, dependencies, fixtures, git, interfaces, orchestration, parallelism, planning, principle, process, provenance, reproducibility, review, testing, verification), kept as a constant in `reindex.py`.
- **New file:** `.githooks/pre-commit` — a shell script that runs `python3 scripts/reindex.py`, and on success `git add`s the regenerated `INDEX.json`; on non-zero exit from the script, aborts the commit without staging anything.
- **One-time repo setup (not code):** `git config core.hooksPath .githooks`, needed once per clone since `.git/hooks/` itself is never tracked by git. Documented in README, not automated by this spec.
- **Out-of-band decision this depends on:** ADR 0004 (Superseded Learnings are never deleted, never back-edited into other files' `links`) and ADR 0009 (tags are a closed vocabulary grown lazily) — this spec implements the mechanics both ADRs already decided.

## Testing Decisions

- Good tests here exercise the build's external behavior — given a temp directory of markdown fixtures, assert on the returned entries / raised failure / emitted warnings — not on frontmatter-parsing regex internals.
- Primary seam: a single pure function, `build_index(learnings_dir) -> (entries, warnings)`, callable against a temp fixture directory with no other filesystem or git side effects. Fixture set should cover: a valid pair of linked files, a dangling `links` id (expect failure), an unrecognized tag (expect a warning, not a failure), two Specifics sharing one Principle (expect `corroboration: 2` on the Principle), and a file with `superseded_by` set (expect passthrough).
- No existing test suite exists in this repo yet — this is the first one. Use stdlib `unittest`, matching `reindex.py`'s existing zero-dependency constraint, rather than introducing `pytest`.
- The `.githooks/pre-commit` shell wrapper is not unit-tested in isolation — a single manual/integration check (introduce a dangling link, attempt a commit, confirm it's blocked; fix it, confirm the commit succeeds and `INDEX.json` is staged) is sufficient given its thinness.

## Out of Scope

- The MCP server and its `search_learnings` / `add_learning` tools (ADR 0008) — separate, future work; see spec 0002.
- Automated redaction or secret scanning (ADR 0006 explicitly deferred this).
- Any change to the content of the 20 existing `learnings/*.md` files.
- CI enforcement (e.g. a GitHub Actions check) — this spec covers the local pre-commit hook only.
- Retroactively backfilling `corroboration` anywhere other than `INDEX.json` — no UI, no README table.

## Further Notes

This is "stage 2" of the pipeline already diagrammed for Sumanth (author → **commit-time build** → repo → retrieval today → future MCP server → agent harness). Stages 1, 3, and 4 already work; stages 5–6 are intentionally untouched by this spec. Stage 5 (the MCP server) is now spec'd separately in spec 0002.
