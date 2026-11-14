---
id: PL-VJD2
title: Build Maximize Area: one Area fills the room the Areas share and the same command restores the layout, with the unconditional region and the disclaimer kept on screen; it waits until the Areas fill the window exactly (PL-CBYS), and docs/interface-provenance.md's adopted entry owes a link to its code
priority: P2
effort: M
status: ready
classes: feature, ux
feature: window-is-the-frame
touches: src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/layout/model.py, src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py
added: 2026-11-11
payoff: a learner can fill the window with one View to study it, and put the layout back with the same command
verify: grep -q 'def test_maximize_area_fills_the_room_and_the_same_command_restores_the_layout' tests/integration/test_simulation_view.py
---

**Problem.** Build Maximize Area: one Area fills the room the Areas share and the same command restores the layout, with the unconditional region and the disclaimer kept on screen; it waits until the Areas fill the window exactly (PL-CBYS), and docs/interface-provenance.md's adopted entry owes a link to its code

**Why it matters.** A learner who wants to study one chart must rearrange a
Workspace to give it room, and then rebuild the arrangement. Blender's
Maximize Area does this with one command and undoes it with the same command.
The project owner adopted it on 2026-11-11 (ratified), and `ROADMAP.md`
planned-milestone entry 34 records the intent.

**Done when.** One command makes one Area fill the room that the Areas
share, and the same command restores the layout exactly as it was. The
unconditional region and the use disclaimer stay on screen. The command is
reachable from the keyboard. The adopted entry in
`docs/interface-provenance.md` links to the code.

**Generator check.** A one-off. It builds a feature the owner adopted, and
no reader misread a fact.
