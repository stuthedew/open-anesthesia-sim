---
id: PL-NV9W
title: Label the alveolar readout end-tidal-equivalent, as MODEL.md requires
priority: P1
effort: S
status: done
classes: safety, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py, docs/MODEL.md
added: 2026-08-30
closed: 2026-09-02
verify: uv run pytest tests/unit/test_simulation_view.py -k end_tidal_equivalent
---

**Problem.** `app/simulation_view.py:488` labels the readout
`"Alveolar / end-tidal"`. `docs/MODEL.md:1067` requires "alveolar or
**end-tidal-equivalent** concentration", and `:1146` states the reason in
terms: "The phrase 'end-tidal-equivalent' must not imply that airway sampling
dynamics, dead space, or capnography are modeled." The shipped label drops the
hedge and asserts the stronger thing the specification forbids.

**Why it matters.** Dead space, airway sampling delay, shunt and
ventilation-perfusion mismatch are all listed as unmodelled at
`docs/MODEL.md:1328-1332`, so the modelled value is not end-tidal in any
patient — it is the alveolar fraction of a single perfectly-mixed alveolar
compartment. "End-tidal" is the name of a *measurement* a clinician reads off a
monitor; using it for a predicted value is the modelled-versus-measured
confusion `CLAUDE.md` calls out directly, and it is the one readout on the
panel a clinician would most readily compare against a real monitor. A correct
number under a label that overstates what it is remains a presentation-safety
failure.

**Where.** `app/simulation_view.py:488`; `docs/MODEL.md:1067` and `:1146`;
`tests/unit/test_simulation_view.py`.

**Priority note.** Captured with a suggested `P2`, raised to `P1`: `safety` is
the right class for a label that misstates what a displayed clinical value is,
and `docket check` will not seat a safety-classed item below `P1`. Demoting the
class to keep the band small would be the wrong trade.

**Approach.** Change the string to the hedged form `docs/MODEL.md` specifies,
and pin it in `tests/unit/test_simulation_view.py` so the hedge cannot be
dropped again by an editing pass. Check the same phrasing in any chart legend
or axis label that names the trace, not only the metric panel.

**Done when.** No interface string calls the modelled alveolar value
"end-tidal" unhedged, the label matches `docs/MODEL.md:1067`, and a test asserts
the exact string.

**Worked.** The label reads `"Alveolar / end-tidal-equivalent"`, and two tests
hold it: one asserts the exact string against the label the grid actually
builds *above that value control*, so the pairing is pinned along with the
wording; the other walks every string in the mounted control tree and fails on
any spelling of "end-tidal" that is not the hedged form, which is what the
"no interface string" clause needs and what covers the legend, the axis caption
and anything added later. Both restate the literal rather than importing it,
so an edit to `simulation_view.py` cannot move both sides of the assertion at
once. `docs/MODEL.md` needed no change: it already carried the requirement,
and the defect was only that the interface did not meet it. The chart legend
was checked and left alone — it says "Alveolar", which makes no end-tidal
claim.

**One thing the brief did not anticipate.** Rendering the running app showed
the required label is too long for an equal share of the readout row: at 1440
CSS pixels it wrapped to "Alveolar / end-tidal-" over "equivalent", which
restored the unhedged phrase for anyone reading the row rather than studying
it, and dropped that one reading below the baseline the other six share. The
alveolar panel is now three grid columns to their two (15 columns in total,
still filling the row exactly), verified by rendering at 1024, 1280 and 1440.
At 1280 and above every label is on one line. At 1024 it wraps again, along
with three labels that already wrapped there before this change; `PL-8M05`
carries that.
