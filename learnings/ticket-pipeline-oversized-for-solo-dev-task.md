---
id: ticket-pipeline-oversized-for-solo-dev-task
date: 2026-09-15
project: observability-integration
tags: [process, planning, efficiency]
type: specific
links: [persist-decisions-the-instant-they-are-confirmed, point-at-files-dont-restate-them, gate-process-ceremony-on-consumer-count, reapply-scale-concern-at-every-stage, judge-spend-by-information-gained-not-size]
---

## Context

Built a full spec → ticket breakdown → dependency-graphed multi-agent dispatch pipeline for a task only I would ever pick up. ~8 decisions got settled once, then re-derived in prose four separate times (spec doc, ticket breakdown, three agent prompts) because no shared file existed for downstream artifacts to point to. "I'll write it once confirmed" was said twice about persisting a decision and never executed. A scale concern flagged up front only got applied to one visible dial (fewer questions), not the shape of the whole pipeline. The one genuinely expensive step that was worth it found a real concurrency bug via an empirical repro, not an assertion.

## Learning

Should have gated the whole pipeline on "will someone other than me pick this up without asking me anything?" before starting, and re-applied that check at every stage. Decisions should have been written to file the instant they were confirmed, with every downstream artifact pointing at that file instead of restating it. Cost should have been judged by what each step actually discovered, not by its size.

## Why it matters

Re-deriving the same ~8 decisions 4 times multiplied the cost of every cold-start boundary crossed. Persisting to file the instant a decision is confirmed would have collapsed all four re-derivations into "read X.md." The pipeline (spec/tickets/multi-agent dispatch) is built for team handoff, not solo work — proportionality to audience wasn't re-checked past the first stage.

## Generalized principle

See [[persist-decisions-the-instant-they-are-confirmed]], [[point-at-files-dont-restate-them]], [[gate-process-ceremony-on-consumer-count]], [[reapply-scale-concern-at-every-stage]], and [[judge-spend-by-information-gained-not-size]].
