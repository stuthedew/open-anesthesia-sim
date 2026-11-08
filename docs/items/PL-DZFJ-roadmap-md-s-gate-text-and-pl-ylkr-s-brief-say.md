---
id: PL-DZFJ
title: ROADMAP.md's gate text and PL-YLKR's brief say every drawn chart point is an M4 representative of a bucket of recorded samples, which PL-2FM6 deleted in v0.4.12 - the chart evaluates the score at the plotted instants
priority: P1
effort: S
status: done
classes: safety, docs
feature: presentation-safety
milestone: v0.4.15
touches: ROADMAP.md, docs/items/PL-YLKR-design-what-a-chart-tooltip-says-fl-chart-s.md
added: 2026-09-12
closed: 2026-09-13
pr: 507
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


**Closed 2026-09-13.** Two paragraphs in `ROADMAP.md`'s v0.5.0 gate section, and
two passages in `PL-YLKR`'s brief.

The admission paragraph no longer argues from M4 decimation. It argues from what
the tooltip says - a bare number with no unit, compartment, agent, or anything
marking the quantity as modelled rather than measured - which is the ground that
survives the correction and which `CLAUDE.md` names in terms under "clearly
distinguish modeled/internal states from measured or directly observable
quantities". The paragraph below it records what the old argument said, that
`PL-2FM6` removed the mechanism in v0.4.12, and that the entry survives because
the *admission* does rather than because the argument did.

`PL-YLKR`'s first obligation changed with it: from "that the point is not a
sample", which is now false, to "that the value is modelled, not measured",
which is a different problem reaching the same remedy. Confirmed against
`app/chart_series.py`, whose module docstring already states the corrected
fact - every drawn point is a state of the run at the instant it is drawn at,
nothing interpolated or synthesized, and a control event always given its own
column.

`PL-YLKR` was `ready` and unstarted when this landed, re-checked against
`origin` at the close, which its done-when required.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-V8SJ`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Debt gate: the frozen list" (Gate 1), at the foot of the group "Added 2026-09-12 under the unconditional safety/science exception — 7 entries". "The paragraph immediately above" and "the paragraph above" are the paragraph "`PL-YLKR` is here for what the tooltip may imply rather than for what it says", "this document" is `ROADMAP.md`, and "the gate" is Gate 1. "`PL-MMWX` above" is that group's paragraph admitting `PL-MMWX`. The group now keeps one paragraph saying that this item corrected that paragraph and `PL-YLKR`'s brief on 2026-09-13.

> **The seventh is the paragraph immediately above** (`PL-DZFJ`, found by the `PL-0QQP` triage pass, 2026-09-12; corrected 2026-09-13). Until that date, the paragraph argued for `PL-YLKR`'s admission from a mechanism the tree no longer has. It said that every drawn point was an M4 representative of its bucket, roughly 120 recorded samples at 300x. It also said that the hover "presents it as the value at that instant". `PL-2FM6` deleted `RunHistory`, `HistoryWindow`, `SimulationHistorySample` and the M4 decimation module in v0.4.12. The chart now evaluates the run's score *at* the instants it plots, and a control event always gets its own column. So when the hover presents a point as the value at that instant, it is correct, not misleading. The gate's stated reason for admitting a `P1` `safety` entry was false. It was false in exactly the direction that made the entry look necessary.

> What survives the correction is the admission, not the argument. That is why this is a rewrite and not a removal. A bare number with no unit, compartment or agent beside it is a presentation-safety matter, whatever produces it. A correct number that carries nothing marking it as modelled is a failure that `CLAUDE.md` names explicitly. The paragraph above now argues that, and `PL-YLKR` stays. It is admitted on the same ground as `PL-MMWX` above. A wrong statement in this document about what a displayed value represents misleads the session that scopes the work, rather than a user. `PL-YLKR`'s own brief carried the same sentence into that work, whose declared `touches` are `docs/MODEL.md`, `README.md` and the chart-series module. The brief was corrected along with this paragraph.
