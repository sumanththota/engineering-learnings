---
id: contract-before-parallelism
date: 2026-09-14
project: n/a
tags: [principle]
type: principle
confidence: confirmed x1
links: [freeze-interface-contract-before-parallel-porting]
---

## Principle

**Contract before parallelism.**

Freeze interfaces/schemas before splitting work across parallel agents or developers.

## Why it matters

Parallel workers without a shared contract diverge independently; integration becomes rework instead of a formality.

## Origin

Derived from [[freeze-interface-contract-before-parallel-porting]] (pdf-ingestion-migration).
