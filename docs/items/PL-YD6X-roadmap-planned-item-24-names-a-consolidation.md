---
id: PL-YD6X
title: ROADMAP planned item 24 names a consolidation prerequisite that is already done: PL-2CS8 moved every display token into app/theme.py and app/controller.py now holds zero module constants and zero core-duplicated defaults, so the stated blocker describes a tree that no longer exists
priority: P2
effort: S
status: ready
classes: docs, defect
feature: settings-panel-prerequisite
touches: ROADMAP.md
added: 2026-09-17
verify: python3 tools/doc_check.py check && ! grep -qF 'Pre-requisite: consolidate the' ROADMAP.md
---

**Problem.** ROADMAP planned item 24 names a consolidation prerequisite that is already done: PL-2CS8 moved every display token into app/theme.py and app/controller.py now holds zero module constants and zero core-duplicated defaults, so the stated blocker describes a tree that no longer exists

**Why it matters.** Item 24 opens by naming a prerequisite that is done, in the
present tense, against a tree that no longer exists - three scattered locations
that were consolidated by `PL-2CS8`. A session scoping the preferences panel
reads it as work still owed before anything can start, which is a wrong answer in
the conservative direction: nobody challenges a blocker, so the milestone looks
further away than it is. `tools/doc_check.py` cannot catch it, because every path
it names still exists and only the tense is false.

It shares a paragraph with `PL-QBX0` (item 24's gate misses the ISO 5360 colours
and the contrast-checked palette), so the two are worked together under
`feature: settings-panel-prerequisite`.

**Done when** item 24 records that the consolidation landed, with the item that
did it, and states any prerequisite that genuinely remains rather than the one
that has been met.
