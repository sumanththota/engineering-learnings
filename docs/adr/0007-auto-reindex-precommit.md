# Reindex runs automatically via pre-commit hook

Unlike redaction (ADR 0006, left manual — it needs judgment), a stale `INDEX.json` fails silently: it's the actual surface an agent searches, so drift between it and `learnings/*.md` produces wrong retrieval results with no visible symptom. A git pre-commit hook runs `reindex.py` and stages the regenerated `INDEX.json` on every commit, so the index can never be committed out of sync with the files it's built from.
