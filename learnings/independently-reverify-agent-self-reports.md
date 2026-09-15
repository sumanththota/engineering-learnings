---
id: independently-reverify-agent-self-reports
date: 2026-09-14
project: pdf-ingestion-migration
tags: [agents, verification, process]
type: specific
confidence: confirmed x1
links: [never-trust-self-report-reverify]
---

## Context

Each porting agent reported its own ticket as complete and tests passing.

## Learning

Don't trust agent self-reports — independently re-run tests and diff the ported code against source before merging.

## Why it matters

Self-reports can be wrong or optimistic without any intent to deceive; the only reliable signal is re-running the check yourself against the actual artifact.

## Generalized principle

See [[never-trust-self-report-reverify]].
