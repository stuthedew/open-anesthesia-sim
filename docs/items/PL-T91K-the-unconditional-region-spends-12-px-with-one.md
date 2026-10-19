---
id: PL-T91K
title: The unconditional region spends 12 px with one run and 24 px with two on notice banners that are hidden, because each run's banner sits in a holder that stays visible and the notice column stays in the run column with its spacing on both sides
priority: P2
effort: S
status: ready
classes: defect, ux
feature: interface-areas
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py, docs/MODEL.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-18
payoff: Compare mode gives the concentration chart back 24 px on a laptop screen where it is already below its minimum height, without hiding any halt or refusal banner
verify: grep -q 'def test_hidden_notice_banners_take_no_height' tests/integration/test_simulation_view.py
---

**Problem.** The unconditional region spends 12 px with one run and 24 px with two on notice banners that are hidden, because each run's banner sits in a holder that stays visible and the notice column stays in the run column with its spacing on both sides

`SimulationView._build_unconditional_region` puts a `notices` widget between
the transport rows and the readouts, and `_place_run` puts each run's banner
in it inside a `_holder`. A hidden banner leaves its holder visible at 0 px,
so the column's 12 px spacing still applies between two holders, and the
`notices` widget still takes the run column's 12 px on each side. Measured
2026-10-18 at 1366 by 700 on the offscreen font while building `PL-QLZ5`: the
two runs' lines and the shared heading stand 24 px further apart than their
spacing needs. The same gap costs one run 12 px.

**Why it matters.** Compare mode leaves the concentration chart about 264 px
on the 1366 by 700 laptop reference, against a 360 px minimum (`PL-JG82`,
`PL-QLZ5`), and every pixel the region spends is one the chart loses.

**Take care.** The halt and refusal banners are safety text, so a fix must
still show each one when it applies. `docs/MODEL.md`'s hazard table describes
the notice column and its 12 px spacing (`PL-TSZM`), so that row is reread with
the fix.

**Checked 2026-10-19.** `_place_run` in `src/anesthesia_sim/app/simulation_view.py`
still places `run.build_notice()` inside a `_holder` in `self._notice_column`,
and `_build_unconditional_region` still adds the `notices` widget to the run
column, as the brief describes.

**Done when.** With every banner hidden, the notice column takes no height and
adds no spacing, for one run and for two. With a banner showing, it appears
where it does today. A test in `tests/integration/test_simulation_view.py`
pins both cases. The hazard-table row in `docs/MODEL.md` that describes the
notice column is reread and corrected if it no longer holds.
