---
id: PL-GJFL
title: Decide whether Shift in an Area border drag should extend the drag to every aligned border as Blender's does, or keep moving the dragged border alone as it does now (found closing PL-ZD8Y)
status: untriaged
added: 2026-11-14
---

**Problem.** Decide whether Shift in an Area border drag should extend the drag to every aligned border as Blender's does, or keep moving the dragged border alone as it does now (found closing PL-ZD8Y)

**What was read.** On 2026-11-14 the Blender Manual's "Areas" page, in its "Resizing" section, said that holding Shift moves nearby aligned borders together while resizing (https://docs.blender.org/manual/en/latest/interface/window_system/areas.html, downloaded whole). `screen_ops.cc` on `blender/blender` `main`, read the same day, passes the Shift state to `area_move_init` as `extend`, and pressing or releasing Shift during a drag turns the extended selection on or off through `area_move_reinit`. Here, Shift does the reverse: `AreaLayout` passes `alone=True` to `LayoutModel.resize`, so only the dragged border moves (`PL-2KXB`), and the keyboard's Shift+arrow does the same. `PL-RQT1` Q3 (ratified 2026-10-11) chose that believing it matched the Manual. `docs/interface-provenance.md` now records it as a divergence with no cause beyond that reading (`PL-ZD8Y`).

**The choice.** Keep Shift as "this border alone", or make it extend the drag to aligned borders that are not connected, as Blender's does. A reader coming from Blender expects the second. The layout model moves only the adjacent collinear borders by default, so an extended drag would need a second selection rule in `LayoutModel.resize`. Changing it alters what a drag does under a reader's hand, which makes it the owner's call under `.claude/rules/instruction-writing.md` rule 14. The look of the interface is not in question, so no screenshot is needed.

**Generator check.** One-off: it follows from one misreading of the Manual in one decision.
