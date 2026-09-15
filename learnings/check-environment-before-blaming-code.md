---
id: check-environment-before-blaming-code
date: 2026-09-14
project: n/a
tags: [principle]
type: principle
confidence: confirmed x1
links: [check-data-provenance-before-assuming-bug]
---

## Principle

**Before assuming code is wrong, check environment and data provenance first.**

When output looks wrong, rule out environment/version/data differences before debugging logic.

## Why it matters

A meaningful fraction of 'bugs' are actually mismatched inputs or environments — checking provenance first is cheaper than a full debugging pass.

## Origin

Derived from [[check-data-provenance-before-assuming-bug]] (pdf-ingestion-migration).
