---
id: persist-decisions-the-instant-they-are-confirmed
date: 2026-09-15
project: n/a
tags: [principle, efficiency]
type: principle
links: []
---

## Principle

**The instant a decision is finalized, persist it to the file its future consumers will actually read — before advancing to the next stage.** No "I'll write it once confirmed" as a mental TODO; confirm and write are one atomic step.

## Why it matters

An intention parked as "later" with no immediate trigger reliably evaporates — attention moves to the next task and nothing calls it back. Collapsing the gap between confirmation and documentation to zero is the only fix that isn't just a good intention.

## Origin

Derived from [[ticket-pipeline-oversized-for-solo-dev-task]] (observability-integration).
