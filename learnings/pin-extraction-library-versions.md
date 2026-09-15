---
id: pin-extraction-library-versions
date: 2026-09-14
project: pdf-ingestion-migration
tags: [dependencies, reproducibility, testing]
type: specific
confidence: confirmed x1
links: [pin-dependency-versions-for-ground-truth]
---

## Context

pypdf was unpinned in the environment used to generate the golden fixture.

## Learning

Unpinned pypdf made the golden fixture unreproducible — a later run against a newer pypdf version produced different output than the recorded fixture.

## Why it matters

Ground-truth data is only ground-truth if the tool version that produced it is fixed; otherwise the fixture silently drifts underneath you.

## Generalized principle

See [[pin-dependency-versions-for-ground-truth]].
