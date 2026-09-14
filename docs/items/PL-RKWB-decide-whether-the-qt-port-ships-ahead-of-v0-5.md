---
id: PL-RKWB
title: Decide whether the Qt port ships ahead of v0.5.0's display half: PL-8PSW is the only scheduled item the port rewrites, and on Flet it is built where no session can look at it
priority: P2
effort: M
status: done
classes: planning
feature: qt-port
touches: ROADMAP.md, docs/items, docs/WORKING_NOTES.md
added: 2026-09-14
closed: 2026-09-14
pr: 573
verify: python3 tools/doc_check.py check && grep -qF 'Moved ahead of v0.5.0' ROADMAP.md
---

**Problem.** Decide whether the Qt port ships ahead of v0.5.0's display half: PL-8PSW is the only scheduled item the port rewrites, and on Flet it is built where no session can look at it

**Raised by the project owner, 2026-09-14**: "Seems like a lot of stuff we are
doing is going to need to be redone (e.g. `PL-8PSW`) after the Qt/PySide port.
Should we move the Qt port up?"

**Counted rather than answered from the shape of the question**, on the same
method § "Sequenced past v0.5.0" used on 2026-09-14 when the general form of
this was asked about the gate entries. Of v0.5.0's 8 open Required-scope ids:

| Item | Touches the rewritten surface? |
| --- | --- |
| `PL-49R8` | no - `.claude/rules` |
| `PL-CTD7` | no - `controller.py`, `core/simulation.py` |
| `PL-B8MK` | no - `controller.py`, `core/run_definition.py` |
| `PL-Z3W6` | no - `tests/`, `docs/MODEL.md` |
| `PL-W7H9` | no - `docs/MODEL.md`, `docs/ARCHITECTURE.md` |
| `PL-RD3B` | partly - durable half is `controller.py`/`run_series.py` |
| `PL-LPLD` | partly - collections in `controller.py`, list widget redrawn |
| `PL-8PSW` | **yes, wholly** |

Exactly three modules import Flet - `simulation_view.py` (4 321 lines),
`chart_series.py` (776) and `main.py` (36) - and
`tools/import_boundary_check.py` is why v0.5.0's landed work (the score,
`PL-J2TD`'s keyframe opening, `PL-TFX5`'s fork, `PL-B9PY`'s decomposition) sits
on the surviving side. **So the premise does not hold on the count: one of
eight, not "a lot".**

**But the conclusion may still be right, on three grounds the premise never
names**, and they are the reason this is a decision rather than a closed
question:

1. **`PL-8PSW` is built blind on Flet.** `PL-2QMK` records that no session in
   the web container can visually confirm a chart change, because Flet's
   renderer fetches Flutter assets the egress proxy denies; `spikes/qt/qt_spike.py
   --screenshot` already renders offscreen in that same container, and
   `PL-YCWZ` adds headless rendering tests over the real Qt interface.
   `PL-7J96`, the Flet equivalent, is `dropped` as superseded - so the Flet
   build gets no automated rendering check at all. `PL-8PSW` is the most
   presentation-safety-loaded item in the milestone (six channels spent, a
   two-compartment cap, every curve attributable to its run) and it is
   scheduled onto the one toolkit that cannot be looked at.
2. **Two `P1` `safety`-classed items are blocked behind the port.** `PL-GS3R`
   (0.26 MAC of drawn departure at the 12 h base, worst in the steep early
   wash-in) and `PL-YVHK` (the hover readout). Both are designed; both wait on
   the toolkit. Ordering v0.5.0 first keeps them blocked for a whole milestone.
3. **The port's parity target is smaller now than after v0.5.0.** Its
   definition of done is "every capability the Flet build has, the Qt build
   has", checkable only against a closed enumeration. Landing v0.5.0 first adds
   compare mode - the largest new visual surface in the project - to that list.

**Against**, and recorded so the decision is not one-sided: v0.5.0 is the MVP
boundary and reordering delays it; Gate 2's freeze was deliberately timed to
v0.5.0 shipping so it would hold v0.5.0's findings, and that timing has to be
re-decided; and § "Items this port moots or transforms" already accepted this
duplication once, for `PL-B9PY`, on the ground that deferring it would defer
the MVP.

**Versioning is not a cost.** § "Versioning decision" picks the number for the
capability boundary crossed, and the port crosses none - so ported first it
takes the next patch number and v0.5.0 keeps both its number and its meaning.

**Decision needed, and it is the project owner's.** The narrow form is not
"move the whole milestone" but: *does anything new get built in
`simulation_view.py` or `chart_series.py` before the port?* `PL-8PSW` and
`PL-LPLD`'s list widget are the only two open items that would.

**Urgency.** A session was opened on `PL-8PSW` at 17:03 on 2026-09-14 and
failed before starting. The next one will not.

**Why it matters.** The sequencing decides whether the most
presentation-safety-loaded item in v0.5.0 is built on a toolkit no session in
this container can look at. `PL-8PSW` draws two runs on one axis with six
channels already spent and a two-compartment cap the design rests on; on Flet
`PL-2QMK` means nobody can see it and `PL-7J96`, the Flet rendering check, is
`dropped` as superseded, so it would ship with no automated rendering check at
all. It also decides how long two `P1` `safety`-classed items stay blocked:
`PL-GS3R` is 0.26 MAC of drawn departure at the 12 h base and `PL-YVHK` is a
hover readout that prints five decimals past the derived resolution, and both
wait only on the toolkit. Getting this wrong is not a lost afternoon - it is a
milestone's worth of safety debt held open and a clinical display built blind.

**Done when** the roadmap places the port ahead of v0.5.0 with the decision and
the count recorded, every item that waited on the port names the port item
rather than a version, `PL-8PSW` and `PL-LPLD` can no longer be started on
Flet, and `make check` is green on the result.

## Decided 2026-09-14 by the project owner: move it

The port goes ahead of v0.5.0's display half. What that means concretely, and
it is narrower than moving the whole milestone: **nothing new is built in
`app/simulation_view.py` or `app/chart_series.py` before the port.** v0.5.0's
port-neutral spine - `PL-CTD7`, `PL-B8MK`, `PL-Z3W6`, `PL-W7H9`, `PL-49R8` -
is unaffected and still ships on the schedule it had.

**The re-point is to items, not to a version, and that is the load-bearing
half.** Seven of the nine entries carrying `blocked-by: v0.5.1` already named
the port item beside the version; the version half is now dropped from all
nine and the remaining two given the item that does the work. `PL-3355`'s own
brief had already argued for this shape, and `PL-16ZC` already used it.

| Item | Now blocked on | Because |
| --- | --- | --- |
| `PL-Q4VH`, `PL-THXF`, `PL-GS3R`, `PL-YVHK` | `PL-G59B` | the chart port |
| `PL-3355`, `PL-TG60`, `PL-QR6Q`, `PL-005`, `PL-LPLD` | `PL-25KS` | the dashboard port |
| `PL-W8DQ`, `PL-NGF7` | `PL-L9RD` | the theme port |
| `PL-8PSW` | `PL-G59B` | the overlay is drawn on the ported chart |

It makes every one of them independent of what number the port ships under,
which is why the numbering question below blocks nothing.

**`PL-005` and `PL-LPLD` carried the deferral in prose alone** and were
`status: ready`, so `bin/docket next` would have offered either - which is
exactly the defect `PL-D143` described for the other five and fixed only for
them. Both are now `blocked` with the field to match.

**Gate 2 needs no re-timing, which is a correction to what this item first
said was owed.** § "v0.5.1" deferred its freeze to when v0.5.0 ships, because
Gate 2 holds v0.5.0's findings and freezing it earlier would freeze an empty
list. Moving the port into the pre-v0.5.0 window does not disturb that: the
port takes no gate of its own, exactly as it did not before, and its findings
go to Gate 2 with v0.5.0's.

**The one question the reorder does open is the number**, and it is recorded
here rather than answered. § "The cadence" says "A gate does not get a
version" and forbids cutting an interim release partway through clearing one -
and five of the port's carried fixes are Gate 1 entries. Two readings:

1. **The port is a milestone that carries gate fixes, not gate work.** §
   "Debt inside the milestone's own scope" already blesses this: the test is
   whether the item appears in the milestone's `Required scope`, and all five
   appear at item 8. It takes the next patch number and ships as its own
   release, which is what v0.2.8 did for machinery at this scale.
2. **The port ships inside v0.5.0 with no version of its own**, which is what
   the cadence prescribes for anything landing between a milestone's
   predecessor and its release.

Reading 1 continues what the roadmap already decided twice and is what is
written up. The hazard it inherits is the one the original section named:
`bin/docket release` offers the next free number to whatever is finished, so a
patch cut before the port lands takes the number and the section's heading
moves to the next free one. That is a rename, not a re-scope.
