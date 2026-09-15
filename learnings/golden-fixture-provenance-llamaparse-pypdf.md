---
id: golden-fixture-provenance-llamaparse-pypdf
date: 2026-09-14
project: pdf-ingestion-migration
tags: [testing, fixtures, provenance]
type: specific
confidence: confirmed x1
links: [record-fixture-provenance]
---

## Context

Golden/characterization fixtures for the parser were recorded using LlamaParse output, but the ported code used a pypdf fallback path.

## Learning

Golden fixtures only prove parity if you know how they were generated. Ours was recorded via LlamaParse; the ported pypdf fallback was guaranteed to mismatch it — that mismatch was provenance, not a bug.

## Why it matters

Time was nearly spent debugging a 'failing' test that was actually comparing two different, legitimately-different extraction engines.

## Generalized principle

See [[record-fixture-provenance]].
