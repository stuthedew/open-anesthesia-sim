---
id: PL-K4MQ
title: core/supported_ranges.py's module docstring says the control record's instants are still annotated float (PL-RCYZ), but PL-RCYZ typed ControlChange.elapsed_s and an adjustment's start and end as CaseInstant, so the docstring and docs/MODEL.md § Supported run length disagree
priority: P2
effort: S
status: done
classes: defect, docs
feature: one-source-of-truth
touches: src/anesthesia_sim/core/supported_ranges.py
deferred-from: v0.7.0 - a new problem: d130a946 (2026-10-25 03:44, after the freeze) typed ControlChange.elapsed_s as CaseInstant and left the docstring saying float
added: 2026-11-03
closed: 2026-11-09
pr: 2076
payoff: a developer reading which values are checked types is told the control record's instants are checked, as the code makes them
verify: ! grep -qF 'instants are still annotated' src/anesthesia_sim/core/supported_ranges.py
reenters: PL-RCYZ
---

**Problem.** core/supported_ranges.py's module docstring says the control record's instants are still annotated float (PL-RCYZ), but PL-RCYZ typed ControlChange.elapsed_s and an adjustment's start and end as CaseInstant, so the docstring and docs/MODEL.md § Supported run length disagree

**Why it matters.** The module docstring tells a developer which values are checked types. It says the control record's instants are plain floats, but `ControlChange.elapsed_s` in `src/anesthesia_sim/app/control_record.py` has been a `CaseInstant` since `PL-RCYZ`. A developer could add a second check that the type already makes, or trust the docstring over `docs/MODEL.md`.

**Reproduced 2026-11-03.** The docstring of `src/anesthesia_sim/core/supported_ranges.py` says "The control record's instants are still annotated `float` (`PL-RCYZ`)", and `ControlChange` declares `elapsed_s: CaseInstant`.

**Done when.** The module docstring no longer says the control record's instants are annotated `float`. It names them among the instants built as `CaseInstant`, or points at the annotations instead of listing them.

**Generator check.** A re-entry of `PL-RCYZ`, closed 2026-10-24. That change typed the record and left this sentence describing the old type (`reenters: PL-RCYZ`).

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem began after Gate 3 froze at `817a4d88`, so the item stays deferred to the next gate, and its `deferred-from:` names the commit that began it. At `817a4d88`, `ControlChange.elapsed_s` was annotated `float`, so the docstring was true. `d130a946` (2026-10-25 03:44) typed it `CaseInstant` and left the docstring stale.

**Done 2026-11-09.** The module docstring of `core/supported_ranges.py` now says the control record's instants are `CaseInstant` too: the instant of each change in `app/control_record.py`, and the start and end of each adjustment in `app/control_timeline.py`.
