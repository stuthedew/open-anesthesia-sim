---
id: PL-MFRN
title: An application-wide Undo, with an Edit menu and Ctrl+Z (Cmd+Z on macOS), covering control changes, marks and branch edits, so a learner can reverse any recent action the same way; the marks-only Undo button of PL-5GX4 deliberately bound no shortcut because nothing else in the app can be undone
priority: P3
effort: L
status: ready
classes: feature
feature: interface-design-review
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py, docs/INTERFACE.md
added: 2026-11-23
filed-pr: 2288
payoff: a learner can reverse any recent action, a dial change included, the same way they would in any desktop application
---

**Problem.** An application-wide Undo, with an Edit menu and Ctrl+Z (Cmd+Z on macOS), covering control changes, marks and branch edits, so a learner can reverse any recent action the same way; the marks-only Undo button of PL-5GX4 deliberately bound no shortcut because nothing else in the app can be undone

**Why it matters.** A learner who changes a dial by mistake today must set it back by hand, and only marks can be undone. One Undo for every recent action is what desktop applications teach a reader to expect.

**Done when.** The design is recorded (which actions are undoable, how an undone control change appears in the run's record, and what Ctrl+Z does while a dial is held), and tests show each action undone through the Edit menu and the shortcut.

**Generator check.** Not owed: the item is new work, classed `feature`.
