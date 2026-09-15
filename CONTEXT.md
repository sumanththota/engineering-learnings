# Engineering Learnings

A personal, general-purpose store of engineering learnings from any project, structured so AI agents can search it.

## Language

**Learning**:
A single captured insight from real engineering work, stored as one file. Every Learning is one of two kinds: Specific or Principle.
_Avoid_: lesson, note, entry

**Specific (learning)**:
A Learning tied to one concrete project and incident — what happened, in that context, at that time.
_Avoid_: case study, incident report

**Principle**:
A generalized, project-agnostic rule that one or more Specific learnings reduce to. Principles are shared: multiple Specific learnings from different, unrelated projects can link to the same Principle rather than each minting a near-duplicate.
_Avoid_: rule, best practice

**Tag**:
A keyword drawn from a closed, canonical vocabulary — not free text. A new tag is a deliberate addition to the list below, not an incidental word choice; `reindex.py` warns on any tag outside it.
_Canonical list_: agents, debugging, dependencies, efficiency, fixtures, git, interfaces, orchestration, parallelism, planning, principle, process, provenance, reproducibility, review, testing, verification

**Superseded**:
A Learning that has been replaced by a newer file with better phrasing or corrected content. Stays in the repo, permanently, with `superseded_by` pointing at its replacement. Other files' `links:` pointing at a Superseded id are not updated — `superseded_by` is the forward breadcrumb. Ranks lower in retrieval, but is never hidden or deleted.

**Corroboration**:
How many Specific learnings independently reduce to a given Principle — a property of the link graph, not something authored by hand.
_Avoid_: confidence (conflates this with epistemic certainty about whether the principle is true — a different axis; see ADR 0002)
