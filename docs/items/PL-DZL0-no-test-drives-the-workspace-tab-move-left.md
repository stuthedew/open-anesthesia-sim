---
id: PL-DZL0
title: No test drives the Workspace tab Move left/right entries or the Area's Split stacked entry from the keyboard
priority: P3
effort: S
status: ready
classes: test
feature: v0.6.0-done-check
touches: tests/integration/test_layout_keyboard.py
added: 2026-10-20
payoff: a regression that drops the keyboard route to moving a Workspace tab or stacking a split fails a test
verify: grep -q 'Move right' tests/integration/test_layout_keyboard.py && grep -q 'Split stacked' tests/integration/test_layout_keyboard.py
---

**Problem.** No test drives the Workspace tab Move left/right entries or the Area's Split stacked entry from the keyboard

**Why it matters.** `/mnt/project-files/v0.6.0/dod-check.md` holds the whole check of v0.6.0's Definition of done, run on 2026-10-20 before the cut. Its second bullet asks that every layout operation is performable from the keyboard. `test_every_layout_operation_is_reachable_from_the_keyboard` drives every other operation by key, but not the Workspace tab menu's Move left and Move right or the Area menu's Split stacked. A throwaway test on 2026-10-20 showed both work by Shift+F10, so the gap is in the tests only.

**Done when.** The keyboard test drives Move left, Move right and Split stacked by key and asserts each one's effect on the layout.
