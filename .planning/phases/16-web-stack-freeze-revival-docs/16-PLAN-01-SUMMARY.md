---
phase: 16
plan: 01
subsystem: docs
tags: [web-stack, legacy, documentation, freeze, revival]
requires: []
provides: [revival-guide, legacy-markers]
affects: [README.md, src/apex/frontend/app.py, src/apex/frontend/__init__.py]
tech-stack:
  added: []
  patterns: []
key-files:
  created:
    - docs/WEB_STACK_REVIVAL_GUIDE.md
  modified:
    - src/apex/frontend/__init__.py
    - src/apex/frontend/app.py
  verified-unmodified:
    - README.md
decisions:
  - "docs/WEB_STACK_REVIVAL_GUIDE.md written as the single source of truth for web stack freeze context, run instructions, and revival roadmap"
  - "README.md already correctly positions TUI as primary (no changes needed)"
  - "Module docstrings in app.py and __init__.py updated to flag Streamlit as LEGACY/OPTIONAL"
metrics:
  duration: "~2m"
  completed: "2026-05-15"
---

# Phase 16 Plan 01: Web Stack Freeze + Revival Docs Summary

**Freeze existing web stack as optional/legacy without deleting project work.**

The Streamlit frontend, FastAPI backend, PostgreSQL/Redis/Docker/K8s infrastructure is all preserved but marked as an optional legacy extension. The revival guide documents what exists, why it was frozen, how to run it, and a 5-phase roadmap for making it primary again.

---

## Tasks Executed

| # | Task | Type | Commit | Files |
|---|------|------|--------|-------|
| 1 | Add web stack revival guide | `execute` | `52cdcf3` | `docs/WEB_STACK_REVIVAL_GUIDE.md` |
| 2 | Mark Streamlit as optional legacy dashboard | `execute` | `6b04a19` | `src/apex/frontend/app.py`, `src/apex/frontend/__init__.py` |

---

## Task 1: Web Stack Revival Guide

**File:** `docs/WEB_STACK_REVIVAL_GUIDE.md` (241 lines)

Covers all 7 components of the frozen web stack:

| Component | What's documented |
|-----------|------------------|
| Streamlit Frontend | Entry point, pages, components, API client, mock data, auth gap |
| FastAPI API | Factory pattern, routes, middleware, missing rate limiting |
| PostgreSQL + pgvector | ORM models, Alembic migrations, async session pattern |
| Redis 8 | LLM cache, circuit breaker, session data |
| Docker Compose Dev Stack | Single-command infra bring-up, persistent volumes |
| K3s + Kustomize | Deployment manifests, multi-arch build, Cloudflare Tunnel |
| OTel + Grafana LGTM | Full observability stack with port reference |

Includes a **5-phase revival roadmap** (Production Hardening → Cost Controls → CI/CD → Observability → UX) with specific action items for each phase.

## Task 2: Legacy Markers

**Files modified:**
- `src/apex/frontend/__init__.py` — docstring updated to clarify optional/legacy status with explicit pointer to TUI CLI + revival guide
- `src/apex/frontend/app.py` — module docstring updated with LEGACY/OPTIONAL warning and revival guide cross-reference

**README.md verified:** Already correctly positions TUI as primary (`uv run apex` first in quickstart, "No PostgreSQL, Redis, or Docker required" note, `(optional/legacy)` labels in architecture table, separate "Optional: Web Stack" section). No changes needed.

---

## Deviations from Plan

None — plan executed exactly as written.

---

## Self-Check

| Check | Result |
|-------|--------|
| `docs/WEB_STACK_REVIVAL_GUIDE.md` exists | PASSED |
| `src/apex/frontend/__init__.py` modified | PASSED |
| `src/apex/frontend/app.py` modified | PASSED |
| README quickstart is TUI-primary | PASSED (verified: `uv run apex` first, no-infra note) |
| Revival guide is actionable | PASSED (exact commands + 5-phase roadmap) |
| `ruff check` passes | PASSED (on both files) |
| Commits on `feat/web-stack-freeze-revival-docs` | PASSED (52cdcf3, 6b04a19) |
| No accidental deletions | PASSED |
| No untracked files | PASSED |
