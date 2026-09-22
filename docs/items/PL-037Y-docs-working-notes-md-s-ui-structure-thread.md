---
id: PL-037Y
title: docs/WORKING_NOTES.md's UI-structure thread glosses PL-NGF7 as 'decides the theme object', which is not what that item is or does
priority: P3
effort: S
status: ready
classes: docs
feature: queue-hygiene
touches: docs/WORKING_NOTES.md
added: 2026-09-14
verify: ! grep -q '`PL-NGF7` decides the theme object' docs/WORKING_NOTES.md && python3 tools/doc_check.py check
---

**Problem.** docs/WORKING_NOTES.md's UI-structure thread glosses PL-NGF7 as 'decides the theme object', which is not what that item is or does

**Why it matters.** The thread "Shelved, then resumed: UI structure/form
mockups" names three items as the structural half of an interface overhaul -
`PL-2CS8` (consolidate the scattered display constants), `PL-NGF7` and
`PL-B9PY` (decompose `SimulationView` so two runs can be rendered at once) -
and glosses the middle one as "decides the theme object". `PL-NGF7` is
`tools/contrast_check.py` can see no disabled-state colour, because none of
them is a constant in `theme.py`, and it is deferred to the Qt port with an
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

**Verified 2026-09-14, and the first of the two readings is the right one.**
`docs/WORKING_NOTES.md:668-669` still glosses the middle item as "`PL-NGF7`
decides the theme object". `PL-NGF7`'s actual title is that
`tools/contrast_check.py` can see no disabled-state colour, because none of them
is a constant in `theme.py`. Those are not the same item, and the paragraph
eleven lines below in the same thread already describes `PL-NGF7` correctly -
"(`contrast_check.py` can see no disabled-state colour) is deferred to
`v0.4.26`, which dissolves it rather than fixing it, and its expected
disposition is `dropped`". So the thread contradicts itself about one id in one
section, which settles it: the gloss is simply wrong rather than evidence of a
missing item.

**Why it matters.** The gloss is inside the record of a project-owner decision
(2026-09-08, the structural half of an interface overhaul), and it is the only
record that decision exists. A reader following the line finds an item that does
something else and cannot tell whether the decision named a third thing that was
never filed - which is expensive to resolve and cheap to prevent.

**`PL-D1RT` is in the same paragraph** and corrects its placement claim. Whoever
lands second should read the other's change rather than re-deriving it; the two
edits are two sentences apart.

**Done when.** The thread describes `PL-NGF7` as what it is, consistently with
the paragraph below it, and the three items named as the structural half are each
glossed accurately.
