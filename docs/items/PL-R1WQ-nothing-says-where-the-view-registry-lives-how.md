---
id: PL-R1WQ
title: Nothing says where the view registry lives, how a view-kind tag is allocated so a class rename does not trip the loud failure meant for a missing view, or how a pure-Python LayoutModel validates a kind tag without importing a Qt view
status: untriaged
feature: interface-areas
added: 2026-09-16
---

**Problem.** Nothing says where the view registry lives, how a view-kind tag is allocated so a class rename does not trip the loud failure meant for a missing view, or how a pure-Python LayoutModel validates a kind tag without importing a Qt view

**Why it matters.** `PL-C842` decided that "a view is registered by kind, never
a subclass" and that a saved workspace naming a view this build lacks must fail
loudly. Both halves rest on a tag whose allocation nobody has specified. If the
tag is derived from the class name or the display title, an ordinary rename
turns every saved workspace into the loud failure that was designed for a
genuinely missing view - so the safety mechanism fires on a refactor, which is
how a loud failure gets routed around and then ignored.

The second half is a boundary question: `PL-C842` puts the LayoutModel in pure
Python with one adapter importing Qt, so the model must validate a kind tag
without importing the view it names.

**Done when.** The registry's location, the tag's allocation rule and its
stability across renames are written down, and the LayoutModel's validation path
is stated in terms that do not require a Qt import.

## Area-model audit (PL-BNYF)

**Disposition: `missing-prereq`.** Surfaced 2026-09-16 by the area-model audit's completeness critic, after the main sweep had closed - which is the critic earning its place rather than a defect in the sweep.
