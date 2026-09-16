---
id: PL-RTG9
title: README carries no attribution line for the Blender-derived workspace/area model, which docs/interface-provenance.md records as belonging there once the area system actually ships
priority: P3
effort: S
status: blocked
classes: docs
feature: interface-areas
blocked-by: PL-W9P6
touches: README.md
added: 2026-09-16
---

**Problem.** README carries no attribution line for the Blender-derived workspace/area model, which docs/interface-provenance.md records as belonging there once the area system actually ships

**Why it matters.** The project's own provenance standard asks for the
attribution although copyright does not, and `docs/interface-provenance.md`
§ "Attribution" records both where it belongs and why `README.md` does not carry
it yet: the area model is a planned milestone and nothing shipped implements it,
so a README sentence would describe software that does not exist. The obligation
is real and its moment is the ship. This is filed so the moment is not missed,
not so the line is written now - which is why it waits on `PL-W9P6` (the
adapter that turns the reserved splitter handles live) rather than being
startable. `PL-NMTF` scoped item 34 into v0.6.0 on 2026-09-16 and closed; the
moment this item waits for is the release in which the shipped interface
actually is the area/workspace model, which is v0.6.0's ship. `PL-9PD6` is the
separate defect: line 94 of the same file already asserts the attribution has
been made.
