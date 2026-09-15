---
id: isolate-parallel-work-units-physically
date: 2026-09-14
project: n/a
tags: [principle]
type: principle
confidence: confirmed x1
links: [git-worktrees-for-parallel-agent-execution]
---

## Principle

**Isolate parallel work units physically.**

Use worktrees, branches, or containers — never share mutable state across concurrent agents or people.

## Why it matters

Shared mutable state under concurrent writers produces silent collisions; physical isolation makes collision structurally impossible.

## Origin

Derived from [[git-worktrees-for-parallel-agent-execution]] (pdf-ingestion-migration).
