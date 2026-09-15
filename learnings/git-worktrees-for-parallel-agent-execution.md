---
id: git-worktrees-for-parallel-agent-execution
date: 2026-09-14
project: pdf-ingestion-migration
tags: [parallelism, git, agents]
type: specific
confidence: confirmed x1
links: [isolate-parallel-work-units-physically]
---

## Context

6 modules ported in parallel, each by its own agent.

## Learning

Git worktrees + one branch per ticket gave true parallel agent execution with no state collision and cheap cleanup.

## Why it matters

Shared working directories between concurrent agents create silent file clobbering; worktrees give each agent its own filesystem view for near-zero cost.

## Generalized principle

See [[isolate-parallel-work-units-physically]].
