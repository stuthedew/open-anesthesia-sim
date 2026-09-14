---
id: PL-RKWB
title: Decide whether the Qt port ships ahead of v0.5.0's display half: PL-8PSW is the only scheduled item the port rewrites, and on Flet it is built where no session can look at it
status: untriaged
added: 2026-09-14
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
