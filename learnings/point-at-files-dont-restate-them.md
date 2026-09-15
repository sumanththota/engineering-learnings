---
id: point-at-files-dont-restate-them
date: 2026-09-15
project: n/a
tags: [principle, efficiency]
type: principle
links: []
---

## Principle

**Every downstream artifact (spec, ticket, agent prompt) written after a decisions file exists should reference it by path, not re-explain the decisions in prose.**

## Why it matters

Cost scales with the number of cold-start boundaries crossed — every subagent, skill invocation, or fresh context window has zero memory of anything not written down. If a decision lives only in chat history, each boundary re-pays the full explanation cost; this is a multiplier that gets worse the more stages/agents a pipeline has.

## Origin

Derived from [[ticket-pipeline-oversized-for-solo-dev-task]] (observability-integration).
