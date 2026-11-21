---
id: PL-FV44
title: Record why the agent accounting's absolute tolerance is 1e-12 L, which no item, comment or commit message states
status: untriaged
touches: src/anesthesia_sim/core/rounding.py
added: 2026-11-21
---

**Problem.** `AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L` in `src/anesthesia_sim/core/rounding.py` is `1e-12` L, and no record says why. The value is already in commit `875ba0850` ("Build v0.1.0 sevo patient simulation", 2026-08-22), which `git log -S'1e-12' --reverse -- src` lists first. Its docstring cited the largest unaccounted amount in a 3600 s run as if that explained it, but the measurement was made on 2026-09-06, after the value was chosen.

**Why it matters.** The tolerance decides when a step is refused for unaccounted agent. `.claude/rules/sources-and-docstrings.md` asks that the reason for a chosen value come from a record, and that an item be filed where the trace finds none.

**What it changes.** Derive the limit from the rounding of the arithmetic it bounds, as `PL-GJ1W` (each comparison picks its own tolerance) does for the relative limit, or state in the docstring that it is a chosen floor and what it was checked against. `docs/MODEL.md` § "Selected method (as implemented)" gives 1.1e-12 L as the largest unaccounted amount in the 3600 s runs of 2026-11-21, which passed on the relative limit.

**Found in.** `PL-MH9J`'s rewording of the code's prose, 2026-11-21.

**Done when.** The docstring gives a reason that a record or a derivation holds.
