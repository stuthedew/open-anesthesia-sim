---
id: PL-T91K
title: The unconditional region spends 12 px with one run and 24 px with two on notice banners that are hidden, because each run's banner sits in a holder that stays visible and the notice column stays in the run column with its spacing on both sides
status: untriaged
added: 2026-10-18
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
