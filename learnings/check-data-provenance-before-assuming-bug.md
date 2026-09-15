---
id: check-data-provenance-before-assuming-bug
date: 2026-09-14
project: pdf-ingestion-migration
tags: [debugging, provenance]
type: specific
confidence: confirmed x1
links: [check-environment-before-blaming-code]
---

## Context

A numeric mismatch surfaced during parity testing between old and new extraction paths.

## Learning

When a numeric mismatch looks like a bug, check environment/data provenance before assuming the code is wrong.

## Why it matters

The mismatch traced back to the LlamaParse-vs-pypdf fixture provenance issue, not a logic error — checking provenance first would have saved a debugging pass.

## Generalized principle

See [[check-environment-before-blaming-code]].
