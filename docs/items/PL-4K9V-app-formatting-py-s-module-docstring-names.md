---
id: PL-4K9V
title: app/formatting.py's module docstring names SimulationHistorySample, which was deleted with the sample store
priority: P3
effort: S
status: ready
classes: docs
feature: documentation-standard
touches: src/anesthesia_sim/app/formatting.py
added: 2026-09-14
verify: uv run pytest tests/unit/test_formatting.py && ! grep -q 'SimulationHistorySample' src/anesthesia_sim/app/formatting.py
---

**Problem.** app/formatting.py's module docstring names SimulationHistorySample, which was deleted with the sample store

`src/anesthesia_sim/app/formatting.py:24` reads "Everything upstream carries
full binary64 - the compartment states, every integration step, every
`SimulationHistorySample` - and the rounding happens exactly once, here." That
class was deleted with the sample store (`PL-2FM6`) and the name appears
nowhere else in `src/`. The sentence's point survives; only its last example
has to change to whatever the drawn window is now called.

Found while working `PL-TFX5`, and left rather than fixed because the file is
outside that item's declared `touches` — the second test of `CLAUDE.md`'s
fix-now rule. `PL-9KP5` is the same rot in `docs/ARCHITECTURE.md`, and the two
are worth doing together.

**Verified 2026-09-14 against `fb60a00`.** `grep -n 'SimulationHistorySample'
src/anesthesia_sim/app/formatting.py` returns line 24, inside the module
docstring: "Everything upstream carries full binary64 - the compartment states,
every integration step, every `SimulationHistorySample` - and the rounding
happens exactly once, here." `grep -rn 'SimulationHistorySample' src/` returns
exactly one other hit, `app/controller.py:234`, and that one is deliberate: it
names `HistoryWindow` to record that `DrawnWindow` replaced it. So this is the
only place in `src/` where the deleted name is still used as though it were a
live one.

**Why it matters.** The docstring is stating the precision guarantee — that
nothing between the solver and the readout rounds — by listing everything
upstream of the formatter. One of the three things it lists no longer exists, so
a reader checking the claim goes looking for a class that is not there and
cannot confirm the list is complete. `PL-X9KD` is the precedent the same
docstring cites two paragraphs earlier: the derivation was restated at four
sites in this package and all four went stale together when the solver changed,
which is why this file cites `docs/MODEL.md` § "Displayed precision" instead of
restating it. This is that failure arriving through the one example the
docstring still carries in its own words.

**Done when.** `src/anesthesia_sim/app/formatting.py`'s module docstring names
what the chart is actually drawn from — the `DrawnWindow` the controller
evaluates, per `app/chart_series.py:447-449` — in place of
`SimulationHistorySample`, the precision claim around it is unchanged, and
`grep -rn 'SimulationHistorySample' src/anesthesia_sim/app/formatting.py`
returns nothing.

**Do not widen it.** The identical sentence appears in `docs/MODEL.md:5841`
("every `SimulationHistorySample` the chart is drawn from"). That instance
belongs to `PL-27H0`, which sweeps the specification and is `safety`-classed;
this item stops at the source file so that the two do not touch the same line
from two branches.
