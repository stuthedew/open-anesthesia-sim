---
id: PL-K4MQ
title: core/supported_ranges.py's module docstring says the control record's instants are still annotated float (PL-RCYZ), but PL-RCYZ typed ControlChange.elapsed_s and an adjustment's start and end as CaseInstant, so the docstring and docs/MODEL.md § Supported run length disagree
status: untriaged
feature: one-source-of-truth
added: 2026-11-03
---

**Problem.** core/supported_ranges.py's module docstring says the control record's instants are still annotated float (PL-RCYZ), but PL-RCYZ typed ControlChange.elapsed_s and an adjustment's start and end as CaseInstant, so the docstring and docs/MODEL.md § Supported run length disagree
