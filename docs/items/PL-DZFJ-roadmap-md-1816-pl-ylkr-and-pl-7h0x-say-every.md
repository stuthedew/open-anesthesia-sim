---
id: PL-DZFJ
title: ROADMAP.md's gate text and PL-YLKR's brief say every drawn chart point is an M4 representative of a bucket of recorded samples, which PL-2FM6 deleted in v0.4.12 - the chart evaluates the score at the plotted instants
priority: P1
effort: S
status: ready
classes: safety, docs
feature: presentation-safety
touches: ROADMAP.md, docs/items/PL-YLKR-design-what-a-chart-tooltip-says-fl-chart-s.md
added: 2026-09-12
verify: python3 tools/doc_check.py check && ! grep -qF 'Every drawn point is an M4 representative' ROADMAP.md
---

**Problem.** ROADMAP.md:1816, PL-YLKR and PL-7H0X say every drawn chart point is an M4 representative of a bucket of recorded samples, which PL-2FM6 deleted in v0.4.12 - the chart evaluates the score at the plotted instants

**Confirmed at triage, 2026-09-12.** `ROADMAP.md:1834` reads "Every drawn point
is an M4 representative of its bucket - at 300x one ...". `PL-2FM6` (delete
`RunHistory` and draw the chart from the score) is `done` and shipped in
v0.4.12, which deleted the M4 decimation module, `RunHistory`, `HistoryWindow`
and `SimulationHistorySample` outright; the chart now evaluates the run's score
at the instants it plots. `PL-YLKR` is open at `ready`, `P1`, classed
`safety, ux`; `PL-7H0X` is `dropped`, so its copy is inert. The v0.4.14 table row
at `ROADMAP.md:77` names this item as the debt and is correct - it is the
sentence at 1834 that is wrong, not the mention of it.

**Where the sentence sits is the finding, and it was not obvious from the
capture.** `ROADMAP.md:1833` is the gate's *admission paragraph* for `PL-YLKR` -
"**`PL-YLKR` is here for what the tooltip may imply rather than for what it
says.**" - and the M4 sentence is the next line, supplying the whole of its
reasoning. So this is not a stray line in planning prose: it is v0.5.0's stated
justification for admitting a `P1` `safety` entry to its frozen debt gate, and
the mechanism it rests on has not existed since v0.4.12.

The reasoning is wrong in a specific direction rather than merely dated. It says
the hover "presents it as the value at that instant" when the chart now *does*
evaluate the score at that instant, so the implied-certainty problem as stated
does not exist. `PL-YLKR` may well still belong in the gate - a bare number with
no unit, compartment or agent beside it is a presentation-safety matter whatever
produces it - but the paragraph has to argue that rather than the M4 case, and
rewriting it is part of this item.

**Why it matters, and why it is `safety` at `P1`.** Nothing shipped is wrong
today: the chart is correct, and no displayed value, axis, label or provenance
line carries this claim. The band follows the subject matter, which is what
`docket.toml`'s `safety_classes` comment means by "may not sit in the lower bands
however small the task looks", and `PL-MMWX` is the direct precedent - `P1`,
`safety, docs, planning`, `touches: ROADMAP.md`, admitted to this same gate under
the unconditional exception for exactly this shape: a wrong or missing statement
in this document about a clinically meaningful quantity, reaching a session
scoping the work rather than reaching a user.

The exposure is one step away and concrete. `PL-YLKR` is startable today, is
`safety`-classed, and its declared work writes into `docs/MODEL.md`, `README.md`
and `chart_series.py` - the three surfaces a reader consults to decide what a
plotted point means. Its brief carries the same false premise. A session
designing the tooltip from it would state that a drawn point summarises a bucket
of roughly 120 recorded samples, which is a provenance claim about a displayed
value, and `CLAUDE.md` is explicit that the correct number with the wrong
provenance is still a safety failure.

**Done when.** `ROADMAP.md`'s `PL-YLKR` admission paragraph describes what the
chart does - the run's score evaluated at the plotted instants, with a control
event given its own column from the keyframe - and argues `PL-YLKR`'s admission
on grounds that survive that correction; `PL-YLKR`'s own brief says the same; and
`PL-YLKR` is not started before this lands.
