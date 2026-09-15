# No automated redaction check — manual review only, for now

The repo is public, so a Learning could accidentally expose a client name, proprietary detail, or secret. We considered a pre-commit grep backstop (email patterns, common secret formats) alongside human review. We're skipping the automated layer for now: Sumanth is the only person who ever writes to this repo (ADR 0005) and already reviews every file before it's added, so a second automated layer isn't pulling its weight yet. Revisit if write-back ever becomes less manual.
