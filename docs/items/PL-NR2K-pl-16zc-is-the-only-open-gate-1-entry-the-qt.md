---
id: PL-NR2K
title: PL-16ZC is the only open Gate 1 entry the Qt port throws away entirely, and it sits in the gate's clearable 23 with no deferral marker, so a session clearing the gate builds a Flet control v0.5.1 deletes
status: untriaged
added: 2026-09-14
---

**Problem.** PL-16ZC is the only open Gate 1 entry the Qt port throws away entirely, and it sits in the gate's clearable 23 with no deferral marker, so a session clearing the gate builds a Flet control v0.5.1 deletes

**Raised by the project owner, 2026-09-14**: "Shouldn't we drop or postpone all
flet related gate items given we are porting to PySide soon?" The general form
of that proposal does not survive the count, and this item is the one case that
does.

**The count, run against Gate 1 on 2026-09-14.** The gate stands at 163
entries, 131 cleared, 32 open — 23 the gate can clear and 9 blocked outside it.

- **Of the 9 blocked outside, 7 are already deferred to the port**: `PL-GS3R`,
  `PL-3355`, `PL-Q4VH`, `PL-TG60`, `PL-W8DQ`, `PL-THXF` and `PL-NGF7`. The
  owner's proposal is, for these, already the state of the queue — taken on
  2026-09-10 and recorded in ROADMAP.md § "Sequenced past v0.5.0". The other
  two are behind the base anesthesia-machine design round and have nothing to do
  with Flet.
- **Of the 23 the gate can clear, 13 never touch the interface at all** —
  docket, doc_check and roadmap-consistency work.
- **Of the 10 that do, 9 survive the port.** Six touch only modules ROADMAP.md
  § "Explicitly out of scope for v0.5.1" names as surviving untouched
  (`controller.py`, `formatting.py`, `playback.py`, `wash_in.py`,
  `control_timeline.py`, `theme.py`, plus `core/`). Three more are *inputs* to
  the port rather than casualties of it: `PL-JRS3` is the port's own Required
  scope item 4 and "the one most likely to stop this cheaply"; `PL-LL9Y` is
  named under "Decisions the port has to make anyway, so they are made
  deliberately rather than by default"; `PL-YLKR`'s gate entry says in terms
  that "the design is toolkit-independent and survives `v0.5.1`; only its
  implementation moves". `PL-B9PY` is a fourth of that kind by an explicit
  owner decision (2026-09-10): it ships on Flet in v0.5.0 and the port owes it
  its shape.
- **That leaves one**: `PL-16ZC`.

**Why `PL-16ZC` is different.** Its whole deliverable is a show/hide control
for the clinical references and the control marks, living entirely inside
`app/simulation_view.py` — 3 734 lines that `v0.5.1` Required scope item 2
rewrites from scratch. The project owner ruled it out of the port on 2026-09-10
because a control that does not exist today is new capability and the port
admits fixes rather than features, and that is right. But the same reasoning
that keeps it out of the port also means building it on Flet first is the one
thing here that is purely thrown away: written now, it is deleted at the port
and written again afterwards.

**It is currently invisible as such.** `status: needs-decision`, no
`blocked-by`, and `bin/docket wave` lists it among the 23 the gate can clear.
The deferral note is in the item file only — which is the shape `PL-D143` was
filed against and `PL-9S30` fixed for the other nine.

**Three dispositions, and the choice is the project owner's**, the same three
`PL-D143` put and on the same reasoning:

1. **Decline it to Gate 2**, which is what `PL-5B1N`, `PL-3JP0` and `PL-HKTB`
   already got for the same reason (ROADMAP.md, triaged 2026-09-13: "v0.5.1
   rewrites the chart on pyqtgraph ... so answering against the Flet chart
   would mean answering twice"). This is the recommendation — it is the
   treatment the project has already chosen twice for this exact shape.
2. **`status: blocked`, `blocked-by: v0.5.1`** — but this is wrong here and is
   recorded so it is not reached for: `blocked-by: v0.5.1` means *ships with
   this milestone* via `MilestoneStates.ships_with`, which reads Required
   scope, and `PL-16ZC` is deliberately not in it.
3. **Leave it**, and accept that a gate-clearing session may build it on Flet.

**Done when** `PL-16ZC` carries a disposition that `bin/docket wave` and
`bin/docket next` can both see without opening the file, and ROADMAP.md's
Gate 1 section records it where the other deferrals are recorded.
