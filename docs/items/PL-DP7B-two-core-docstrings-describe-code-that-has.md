---
id: PL-DP7B
title: Two core/ docstrings describe code that has changed: AgentUptakeSystem.advance in core/uptake_system.py still describes five sub-exchanges in sequence where _advance_step makes one exact propagation, and RunDefinition._require_within_run says _segment_index_at handles a span before the opening silently where it raises (found rewriting src/ prose for PL-1K5X)
priority: P2
effort: S
status: ready
classes: docs
feature: stale-source-claims
touches: src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/run_definition.py
added: 2026-10-25
payoff: a reviewer checking the core's numerical method against docs/MODEL.md reads a docstring that describes the method the code runs
verify: ! grep -qF 'applies five' src/anesthesia_sim/core/uptake_system.py && ! grep -qF 'would handle that span silently' src/anesthesia_sim/core/run_definition.py
---

**Problem.** Two core/ docstrings describe code that has changed: AgentUptakeSystem.advance in core/uptake_system.py still describes five sub-exchanges in sequence where _advance_step makes one exact propagation, and RunDefinition._require_within_run says _segment_index_at handles a span before the opening silently where it raises (found rewriting src/ prose for PL-1K5X)

**Reproduced 2026-10-25.** `grep` on `main` at `b6ff4443` finds `core/uptake_system.py` line 251 saying `_advance_step()` "applies five sub-exchanges in sequence", while `_advance_step`'s own docstring (line 395) says it advances "every compartment at once, by one exact propagation". `core/run_definition.py` line 901 still says `_segment_index_at` "would handle that span silently".

**Why it matters.** These docstrings describe the numerical method of the core. A reviewer checking the integrator against `docs/MODEL.md` reads them first. A docstring describing a sequential split that the code no longer performs misstates how each step is computed, and why the step is all-or-nothing.

**Done when.** `AgentUptakeSystem.advance` describes the single exact propagation and says what can still reject a step. `RunDefinition._require_within_run` says what `_segment_index_at` does with a span before the opening. Both agree with `docs/MODEL.md`. No behaviour changes.
