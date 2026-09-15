---
id: thin-orchestrator-delegates-execution
date: 2026-09-14
project: n/a
tags: [principle]
type: principle
confidence: confirmed x1
links: [orchestrator-never-writes-ticket-code]
---

## Principle

**The orchestrator never does implementation work itself.**

Keep the coordinating layer thin; delegate execution to scoped, disposable workers.

## Why it matters

An orchestrator that implements accumulates unrelated context, slows down, and risks bleeding state between unrelated units of work.

## Origin

Derived from [[orchestrator-never-writes-ticket-code]] (pdf-ingestion-migration).
