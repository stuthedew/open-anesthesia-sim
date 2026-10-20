---
id: PL-RTG9
title: README carries no attribution line for the Blender-derived workspace/area model, which docs/interface-provenance.md records as belonging there once the area system actually ships
priority: P3
effort: S
status: done
classes: docs
feature: interface-areas
touches: README.md
added: 2026-09-16
closed: 2026-10-20
pr: 1700
verify: grep -q 'Blender is developed by the Blender Foundation' README.md
---

**Problem.** README carries no attribution line for the Blender-derived workspace/area model, which docs/interface-provenance.md records as belonging there once the area system actually ships

**Why it matters.** The project's own provenance standard asks for the
attribution although copyright does not, and `docs/interface-provenance.md`
§ "Attribution" records both where it belongs and why `README.md` does not carry
it yet: the area model is a planned milestone and nothing shipped implements it,
so a README sentence would describe software that does not exist. The obligation
is real and its moment is the ship. This is filed so the moment is not missed,
not so the line is written now, which is why it is not startable. `PL-W9P6`
(the adapter that turned the reserved splitter handles live) closed on
2026-10-18, so `blocked-by` now names the release itself. `PL-NMTF` scoped item 34 into v0.6.0 on 2026-09-16 and closed; the
moment this item waits for is the release in which the shipped interface
actually is the area/workspace model, which is v0.6.0's ship. `PL-9PD6` is the
separate defect: line 94 of the same file already asserts the attribution has
been made.

**Done when.** `README.md` carries the attribution in a section of its own, and `docs/interface-provenance.md` § "Attribution" says it does.
