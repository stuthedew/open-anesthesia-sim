---
id: PL-K4MQ
title: core/supported_ranges.py's module docstring says the control record's instants are still annotated float (PL-RCYZ), but PL-RCYZ typed ControlChange.elapsed_s and an adjustment's start and end as CaseInstant, so the docstring and docs/MODEL.md § Supported run length disagree
priority: P2
effort: S
status: ready
classes: defect, docs
feature: one-source-of-truth
touches: src/anesthesia_sim/core/supported_ranges.py
deferred-from: v0.7.0 - a stale docstring found after the gate cleared
added: 2026-11-03
payoff: a developer reading which values are checked types is told the control record's instants are checked, as the code makes them
verify: ! grep -qF 'instants are still annotated' src/anesthesia_sim/core/supported_ranges.py
reenters: PL-RCYZ
---

**Problem.** core/supported_ranges.py's module docstring says the control record's instants are still annotated float (PL-RCYZ), but PL-RCYZ typed ControlChange.elapsed_s and an adjustment's start and end as CaseInstant, so the docstring and docs/MODEL.md § Supported run length disagree

**Why it matters.** The module docstring tells a developer which values are checked types. It says the control record's instants are plain floats, but `ControlChange.elapsed_s` in `src/anesthesia_sim/app/control_record.py` has been a `CaseInstant` since `PL-RCYZ`. A developer could add a second check that the type already makes, or trust the docstring over `docs/MODEL.md`.

**Reproduced 2026-11-03.** The docstring of `src/anesthesia_sim/core/supported_ranges.py` says "The control record's instants are still annotated `float` (`PL-RCYZ`)", and `ControlChange` declares `elapsed_s: CaseInstant`.

**Done when.** The module docstring no longer says the control record's instants are annotated `float`. It names them among the instants built as `CaseInstant`, or points at the annotations instead of listing them.

**Generator check.** A re-entry of `PL-RCYZ`, closed 2026-10-24. That change typed the record and left this sentence describing the old type (`reenters: PL-RCYZ`).
