---
id: push-to-origin-only-at-review-gates
date: 2026-09-14
project: pdf-ingestion-migration
tags: [git, process]
type: specific
confidence: confirmed x1
links: [decouple-commit-from-publish]
---

## Context

6 tickets landing in parallel, each producing multiple local commits before review.

## Learning

Push to origin only at review gates, not per ticket — local churn stays cheap and reversible; push is the deliberate, visible action.

## Why it matters

Pushing every intermediate commit pollutes shared history and makes it harder to reset course before something becomes externally visible.

## Generalized principle

See [[decouple-commit-from-publish]].
