---
id: PL-W3DD
title: Key SimulationHistorySample by substance rather than six flat compartment floats
priority: P2
effort: M
status: ready
classes: refactor
feature: teachable-case
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/chart_downsampling.py, docs/MODEL.md, tests/unit/test_simulation_view.py
added: 2026-09-02
verify: uv run pytest tests/unit/test_simulation_view.py && grep -q 'def test_history_sample_is_keyed_by_substance' tests/unit/test_simulation_view.py
---

**Problem.** `SimulationHistorySample` (`app/controller.py:17-26`) is a frozen
dataclass of `elapsed_s` plus six flat named floats, one per compartment. Six
module-level accessors in `app/simulation_view.py:209-235` unpack them, one
function per compartment, and `chart_downsampling.py` consumes them through
those accessors. There is exactly one substance today, so nothing about that
shape is wrong yet.

**Why it matters.** `ROADMAP.md`'s v0.4.0 Required scope names this change and
states why (`:1386`): planned-milestone item 12 (forking) writes its
element-wise reproducibility proof directly against this record's shape.
Reshaping the record *after* that proof exists means reworking an
already-validated safety property; reshaping it before is a plain refactor of a
record that no proof yet depends on. Planned-milestone item 6 (nitrous oxide)
needs a second substance in the same record, and doing this first makes the MAC
readout (`PL-DHV7`) a fold over substances rather than a rewrite.

This changes representation, not behavior. No displayed value, unit or label
changes, which is what the existing view tests are for.

**Where.** `app/controller.py` (`SimulationHistorySample`,
`SimulationSnapshot.concentration_history`, `_build_history_sample`),
`app/simulation_view.py` (`:209-235`, the six accessors, and the
trace-to-quantity pairing in `_refresh_chart_series`),
`app/chart_downsampling.py`, `docs/MODEL.md` § "Interface boundary".

**Approach.** Key the recorded concentrations by substance id, keeping
`elapsed_s` flat: the sample carries one entry per substance, each holding the
six compartment values. The six accessors collapse into one parameterized by
compartment, which is what makes adding a substance a data change rather than
six more functions. Do not add a second substance here — this item establishes
the shape, and `core/` still holds one agent.

**Not gate work.** The flat record predates the 2026-08-25 freeze, so
`ROADMAP.md`'s presence presumption would admit it to Gate 0 — but that gate is
closed and v0.3.0 has shipped, and a shipped gate does not reopen. It is
milestone work under "Debt inside the milestone's own scope": the milestone's
Required scope names it, so v0.4.0 clears it, exactly as it does the six gate-0
entries listed under "Cleared by v0.4.0 itself".

**Found.** 2026-09-02, answering "how do we get to v0.4.0". It was the one
Required-scope bullet in the milestone with no queue item behind it:
`docket feature teachable-case` reported 11 items against 12 scope bullets, and
the milestone's Definition of done did not name it either, so it could have
been missed twice. Both are corrected in the same change that files this.

**Done when.** The recorded history is keyed by substance, the six per-compartment
accessors are one accessor parameterized by compartment, `docs/MODEL.md` states
the record's shape at the interface boundary, and every existing view and
downsampling test passes unaltered.
