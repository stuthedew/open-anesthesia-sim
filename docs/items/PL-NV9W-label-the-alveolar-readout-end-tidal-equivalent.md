---
id: PL-NV9W
title: Label the alveolar readout end-tidal-equivalent, as MODEL.md requires
priority: P1
effort: S
status: ready
classes: safety, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py, docs/MODEL.md
added: 2026-08-30
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
