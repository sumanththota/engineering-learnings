---
id: gate-business-logic-tickets-on-human-signoff
date: 2026-09-14
project: pdf-ingestion-migration
tags: [review, process, agents]
type: specific
confidence: confirmed x1
links: [gate-semantic-changes-on-human-review]
---

## Context

Migration tickets split into mechanical ports (pure code movement) and business-logic/integration tickets (behavior changes).

## Learning

Business-logic/integration tickets need human sign-off regardless of test pass; mechanical ports don't need it.

## Why it matters

Tests can pass while still encoding the wrong business decision — mechanical correctness and semantic correctness are different questions, and only a human can answer the second one reliably.

## Generalized principle

See [[gate-semantic-changes-on-human-review]].
