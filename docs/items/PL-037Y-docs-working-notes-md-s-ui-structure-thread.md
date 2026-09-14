---
id: PL-037Y
title: docs/WORKING_NOTES.md's UI-structure thread glosses PL-NGF7 as 'decides the theme object', which is not what that item is or does
status: untriaged
added: 2026-09-14
---

**Problem.** docs/WORKING_NOTES.md's UI-structure thread glosses PL-NGF7 as 'decides the theme object', which is not what that item is or does

**Why it matters.** The thread "Shelved, then resumed: UI structure/form
mockups" names three items as the structural half of an interface overhaul -
`PL-2CS8` (consolidate the scattered display constants), `PL-NGF7` and
`PL-B9PY` (decompose `SimulationView` so two runs can be rendered at once) -
and glosses the middle one as "decides the theme object". `PL-NGF7` is
`tools/contrast_check.py` can see no disabled-state colour, because none of
them is a constant in `theme.py`, and it is deferred to `v0.5.1` with an
expected disposition of `dropped`. So a reader following that line either finds
a different item than the sentence promised, or - if an item that really was to
decide the theme object was meant - finds that it does not exist.

**Why it is not a typo fix.** Which of the two it is decides what to do. If the
gloss is simply wrong, correct the line. If the roadmap decision of 2026-09-08
counted a theme-object decision as part of the structural half and no item
carries it, then one is missing and the thread is the only record that it was
ever wanted - which is the case worth catching, since `v0.5.x - the interface
pass` is where it would be worked.

**Where.** `docs/WORKING_NOTES.md`, the "Shelved, then resumed: UI
structure/form mockups" thread.

**Done when.** The line names an item that exists and does what the line says,
or a missing item has been filed and the line points at it.
