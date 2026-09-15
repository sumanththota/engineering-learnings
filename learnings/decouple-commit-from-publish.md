---
id: decouple-commit-from-publish
date: 2026-09-14
project: n/a
tags: [principle]
type: principle
confidence: confirmed x1
links: [push-to-origin-only-at-review-gates]
---

## Principle

**Decouple "commit" from "publish".**

Iterate cheaply and locally; push, deploy, or release only at defined gates.

## Why it matters

Local commits are free to rewrite; anything pushed/deployed is visible and costly to unwind, so the two should not happen at the same cadence.

## Origin

Derived from [[push-to-origin-only-at-review-gates]] (pdf-ingestion-migration).
