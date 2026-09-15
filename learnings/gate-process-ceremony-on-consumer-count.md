---
id: gate-process-ceremony-on-consumer-count
date: 2026-09-15
project: n/a
tags: [principle, efficiency]
type: principle
links: []
---

## Principle

**Before the first heavyweight artifact (spec, ticket breakdown, dependency-graphed multi-agent dispatch), ask explicitly: will anyone other than me consume this without asking me something?** No → skip straight to implementation or a lightweight checklist.

## Why it matters

Each stage of a pipeline looks locally justified from inside the stage ("we have a spec, so tickets are the natural next step"), so nothing forces a step-back check of whether the whole chain is proportionate to the audience. This is process momentum — the ceremony equivalent of scope creep — and it's insidious because no single step looks wrong.

## Origin

Derived from [[ticket-pipeline-oversized-for-solo-dev-task]] (observability-integration).
