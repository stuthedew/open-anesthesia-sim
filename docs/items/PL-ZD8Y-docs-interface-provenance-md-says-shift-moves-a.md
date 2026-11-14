---
id: PL-ZD8Y
title: docs/interface-provenance.md says Shift moves a border alone here, the reverse of Blender, only in the keyboard entry; the border-chain entry says nothing about Shift, and no divergence is recorded (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: ready
classes: defect, docs
feature: interface-provenance-structure
touches: docs/interface-provenance.md
added: 2026-11-05
payoff: a reader learns what Shift does to a border drag here and how it compares with Blender, from one consistent record
verify: grep -qE '^\*\*Shift' docs/interface-provenance.md
---

**Problem.** docs/interface-provenance.md says Shift moves a border alone here, the reverse of Blender, only in the keyboard entry; the border-chain entry says nothing about Shift, and no divergence is recorded (copy editor structure read, 2026-11-05)

**The structure read's query** (row numbers are docs/interface-provenance.md at cfb15a4a, before the line edit):

- **Query on the Shift key:** rows 294-303 say that in Blender, Shift extends a border drag to every aligned border. Rows 1056-1069 say that here "Shift moves it alone, as in a drag", but the border-chain entry (rows 1013-1036) says nothing about Shift. The reader needs this project's Shift behaviour in rows 1013-1036. Does it reverse Blender's on purpose, as a recorded divergence?

**Checked 2026-11-09:** `grep -n 'Shift' docs/interface-provenance.md` finds Blender's Shift in § "How a layout is built, and how far the operations reach". From `screen_ops.cc`, it says Shift extends a border drag to every aligned border, connected or not. This project's Shift appears only in the keyboard entry: "With Shift held, the border moves alone, as it does in a drag with Shift." The Adopted entry "A drag moves every border on the dragged line, as in Blender" still says nothing about Shift, and no entry in § "Diverged" records it. The code does what the keyboard entry says: `AreaLayout` passes `alone=True` to `LayoutModel.resize` when Shift is held (`PL-2KXB`). The decision behind it, `PL-RQT1` Q3 (ratified 2026-10-11), says "Shift to move only the border under the pointer is kept as Blender has it", citing the Manual's areas page. So the decision meant to follow Blender, while this document's reading of Blender's source says Blender's Shift does the reverse.

**Why it matters.** A contributor or a Blender user who reads only the border-drag entry will expect Blender's behaviour. The document also disagrees with the decision record about what Blender does, and a reader cannot tell which reading is right.

**Done when.** The border-drag entry says what Shift does here. The Manual's areas page and `screen_ops.cc` are read again, and the document says what Blender's Shift does, with the reading date. If Blender's Shift extends the drag, § "Diverged, and each divergence has a specific cause" has an entry led "**Shift**". It says that Shift moves the dragged border alone here, that `PL-RQT1` Q3 chose this believing it matched Blender, and what the Manual says. If Blender's Shift moves one border alone, § "How a layout is built" is corrected instead, and the "**Shift**" entry goes in § "Adopted". Whether to change what Shift does here is not part of this item.

**Generator check.** One-off: a finding from the `docs/interface-provenance.md` structure read (`PL-ZMBN`).

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** `git show 817a4d88:docs/interface-provenance.md` already says Blender's Shift extends a drag ("Extend-drag is the Shift key", row 293) and that here "Shift moves it alone" (row 930), with no divergence recorded. So the problem was present at the freeze, commit `817a4d88` (2026-10-24), and this finding belongs on v0.7.0's frozen list rather than deferred.

**Done 2026-11-14.** The Manual's "Areas" page (https://docs.blender.org/manual/en/latest/interface/window_system/areas.html, downloaded whole, page dated 2026-11-14) says, in its "Resizing" section, that holding Shift moves nearby aligned borders together while resizing. `screen_ops.cc` on `blender/blender` `main` (downloaded whole the same day) agrees: `area_move_invoke` passes `event->modifier & KM_SHIFT` to `area_move_init` as `extend`, and `area_move_modal` calls `area_move_reinit` when Shift is pressed or released during a drag. So Blender's Shift extends a drag, and `PL-RQT1` Q3 misread the Manual. `docs/interface-provenance.md` now dates that reading in § "How a layout is built, and how far the operations reach", says in the border-drag entry what Shift does here, and adds the "**Shift**" entry to § "Diverged, and each divergence has a specific cause" beside it. Whether to change what Shift does is filed as `PL-GJFL`.

Files checked for statements about Shift on a border drag: `docs/interface-provenance.md`, `docs/INTERFACE.md`, `docs/ARCHITECTURE.md`, `ROADMAP.md`, `README.md`, and the module docstring of `src/anesthesia_sim/app/area_layout.py`. None but the first claimed anything about Blender's Shift.
