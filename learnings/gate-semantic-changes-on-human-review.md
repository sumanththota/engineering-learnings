---
id: gate-semantic-changes-on-human-review
date: 2026-09-14
project: n/a
tags: [principle]
type: principle
confidence: confirmed x1
links: [gate-business-logic-tickets-on-human-signoff]
---

## Principle

**Gate semantic changes on human review; let mechanical ones pass on tests alone.**

Distinguish pure mechanical changes (safe to trust to tests) from business-logic/behavioral changes (need a human).

## Why it matters

Tests verify code does what it was written to do, not that what it was written to do is correct — only a human judges the latter.

## Origin

Derived from [[gate-business-logic-tickets-on-human-signoff]] (pdf-ingestion-migration).
