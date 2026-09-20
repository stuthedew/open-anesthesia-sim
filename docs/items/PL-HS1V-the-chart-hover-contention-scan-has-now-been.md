---
id: PL-HS1V
title: The chart-hover contention scan has now been rebuilt from scratch three times - PL-MN4J, PL-JVHL and PL-0RZ0 - and PL-QYBW's axis decision will want it a fourth
status: untriaged
feature: compartment-trace-legibility
added: 2026-09-20
---

**Problem.** The chart-hover contention scan has now been rebuilt from scratch three times - PL-MN4J, PL-JVHL and PL-0RZ0 - and PL-QYBW's axis decision will want it a fourth

Three sessions have now written the same scan into a scratch file and thrown it
away: `PL-MN4J` (whether the box names the run), `PL-JVHL` (the run flip, whose
own table of five targeting rules is the largest of the three) and `PL-0RZ0`
(the compartment flip, 2026-09-20). Each rebuilt the same four things - the
branched sevoflurane case with a keyframe at the fork, the pixel mapping from
`start_s`/`axis_top_percent` and `theme.CHART_HEIGHT`, a replica of
`nearest_trace_point`'s selection fast enough to walk 324,000 pointer
positions, and a check that the replica agrees with the real function.

`PL-QYBW` (the shared percent axis compressing the slow compartments) is a
`needs-decision` design round whose whole question is what the compression
costs a reader, so it wants the same scan a fourth time, and any targeting
change made under `PL-0RZ0` wants it again to score the result.

**What would make it worth building, and what would not.** The decidable half
is the scan: given a frame, a plot size and a radius, which traces are in
reach at each pixel, which is aimed at, and what a 2 px move changes. That
answers identically every run and is exactly what `CLAUDE.md`'s
deterministic-tooling section says to move out of the model. The judgment half
- which cases to score, which metric answers the question, what the number
means - stays in the session and must not be scripted.

Two constraints a design has to meet. `tools/` is standard library only, so the
numpy replica three sessions have used cannot go there as written: either a
slower pure-stdlib scan scoped to the cases that matter, or it lives under
`tests/` where the project virtualenv is available. And it measures the
simulator, so whichever bar applies is worth settling before it is built rather
than after.
