---
id: PL-GJFL
title: Decide whether Shift in an Area border drag should extend the drag to every aligned border as Blender's does, or keep moving the dragged border alone as it does now (found closing PL-ZD8Y)
priority: P3
effort: M
status: needs-decision
classes: ux
feature: interface-provenance-structure
touches: src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/layout/model.py, docs/INTERFACE.md, docs/interface-provenance.md, tests/unit
deferred-from: v0.7.0 - present at the freeze, deferred on a stated reason: it is a choice about what a border drag does, which shows no clinical value; PL-ZD8Y, the frozen entry it follows, only had to record the divergence and is complete without this answer; and no Required-scope work of v0.7.0 touches the layout
added: 2026-11-14
payoff: A reader who knows Blender gets the Shift-drag they expect, or the difference is one the owner chose and the provenance note says why.
---

**Problem.** Decide whether Shift in an Area border drag should extend the drag to every aligned border as Blender's does, or keep moving the dragged border alone as it does now (found closing PL-ZD8Y)

**What was read.** On 2026-11-14 the Blender Manual's "Areas" page, in its "Resizing" section, said that holding Shift moves nearby aligned borders together while resizing (https://docs.blender.org/manual/en/latest/interface/window_system/areas.html, downloaded whole). `screen_ops.cc` on `blender/blender` `main`, read the same day, passes the Shift state to `area_move_init` as `extend`, and pressing or releasing Shift during a drag turns the extended selection on or off through `area_move_reinit`. Here, Shift does the reverse: `AreaLayout` passes `alone=True` to `LayoutModel.resize`, so only the dragged border moves (`PL-2KXB`), and the keyboard's Shift+arrow does the same. `PL-RQT1` Q3 (ratified 2026-10-11) chose that believing it matched the Manual. `docs/interface-provenance.md` now records it as a divergence with no cause beyond that reading (`PL-ZD8Y`).

**The choice.** Keep Shift as "this border alone", or make it extend the drag to aligned borders that are not connected, as Blender's does. A reader coming from Blender expects the second. The layout model moves only the adjacent collinear borders by default, so an extended drag would need a second selection rule in `LayoutModel.resize`. Changing it alters what a drag does under a reader's hand, which makes it the owner's call under `.claude/rules/instruction-writing.md` rule 14. The look of the interface is not in question, so no screenshot is needed.

**Checked 2026-11-22**, at `d4e8200c`. `grep -n 'alone=' src/anesthesia_sim/app/area_layout.py`
printed line 2699, `alone=bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)`,
so Shift still moves the dragged border alone.

**Why it matters.** A reader who knows Blender, whose layout this one follows,
expects Shift to widen a drag, and here it narrows one. The only reason on
record for the difference is a misreading of Blender's Manual, so the
interface diverges from its model for no reason anyone chose.

**Decision needed.** When a reader holds Shift while dragging an Area border,
should the drag also move the aligned borders that are not connected to it, as
Blender does, or keep moving the dragged border alone, as it does now?

**Recommendation:** follow Blender. The divergence rests only on the misread
Manual, and the rest of the layout follows Blender, so a reader's habit from
Blender carries over. The cost is a second selection rule in
`LayoutModel.resize`, a change to what Shift+arrow does from the keyboard, and
the loss of the "this border alone" drag, which Blender does not offer either.
It is the owner's call because it changes what a drag does under a reader's
hand.

**Done when.** The interface does what the owner chose under Shift, for the
pointer and for the keyboard. `docs/INTERFACE.md` and
`docs/interface-provenance.md` state it, and the provenance note records
either that it matches Blender or the owner's reason for the difference. A
test shows the chosen drag.

**Generator check.** One-off: it follows from one misreading of the Manual in one decision.
