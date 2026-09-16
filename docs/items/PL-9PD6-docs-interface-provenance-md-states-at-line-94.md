---
id: PL-9PD6
title: docs/interface-provenance.md states at line 94 that README.md records the Blender attribution and at its Attribution section that README.md deliberately does not yet carry it, which is the contradiction PL-RTG9 was refuted against
priority: P2
effort: S
status: done
classes: defect, docs
feature: interface-areas
touches: docs/interface-provenance.md
added: 2026-09-16
closed: 2026-09-16
pr: 629
verify: python3 tools/doc_check.py check && grep -qF 'and `README.md` does not yet' docs/interface-provenance.md
---

**Problem.** docs/interface-provenance.md states at line 94 that README.md records the Blender attribution and at its Attribution section that README.md deliberately does not yet carry it, which is the contradiction PL-RTG9 was refuted against

**Why it matters.** `docs/interface-provenance.md:94` asserts as fact that
"`README.md` and `ROADMAP.md` item 34 record that the workspace / area / editor
model is modelled on Blender's". The same file's § "Attribution" says the
opposite in terms: "`README.md` does not yet carry this line, deliberately",
with the reason - the area model is a planned milestone and nothing shipped
implements it, so a README sentence would describe software that does not exist.

`README.md` carries no such line today. The provenance document is the one a
session building the layout is told to read first, and it contradicts itself
about what the project has already published - which is the kind of statement
`CLAUDE.md`'s docs-sweep rule treats as a safety matter rather than tidiness,
because the next session to act on line 94 would believe an attribution
obligation was already discharged.

**Done when.** Line 94 states what is actually true today - `ROADMAP.md` item 34
records it and `README.md` does not yet - and points at `PL-RTG9` for the line
that lands when the area system ships.

## Area-model audit (PL-BNYF)

**Disposition: `missing-prereq`.** Surfaced 2026-09-16 by the area-model audit's completeness critic, after the main sweep had closed - which is the critic earning its place rather than a defect in the sweep.
