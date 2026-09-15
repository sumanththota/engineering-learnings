---
id: freeze-interface-contract-before-parallel-porting
date: 2026-09-14
project: pdf-ingestion-migration
tags: [parallelism, interfaces, agents]
type: specific
confidence: confirmed x1
links: [contract-before-parallelism]
---

## Context

Migration split 6 modules across parallel porting tickets, each handled by a separate agent/worktree.

## Learning

Freezing the interface contract (function signatures, I/O shapes) before any module started porting meant all 6 modules integrated with zero surprises at merge time.

## Why it matters

Without a frozen contract, parallel workers guess at boundaries independently and diverge — integration becomes a second full pass instead of a formality.

## Generalized principle

See [[contract-before-parallelism]].
