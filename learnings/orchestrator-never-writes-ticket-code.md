---
id: orchestrator-never-writes-ticket-code
date: 2026-09-14
project: pdf-ingestion-migration
tags: [agents, orchestration, process]
type: specific
confidence: confirmed x1
links: [thin-orchestrator-delegates-execution]
---

## Context

One session coordinated all 6 porting tickets across agents.

## Learning

The orchestrator session never wrote ticket code itself — every ticket ran as a fresh Agent call. This kept the orchestrator's context small and prevented drift.

## Why it matters

An orchestrator that also implements accumulates context from every ticket, gets slower and more error-prone, and starts blending unrelated tickets' state together.

## Generalized principle

See [[thin-orchestrator-delegates-execution]].
