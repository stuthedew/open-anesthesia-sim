---
id: PL-G05S
title: Rename two docs/INTERFACE.md headings that code comments and a test cite: § "What is not bounded this way" covers only the two volumes, and § "MAC-awake as a chart reference" also holds the 1 MAC line
priority: P3
effort: S
status: ready
classes: docs
feature: prose-quality
touches: docs/INTERFACE.md, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/theme.py, tests/reference/test_mac_awake_washout_figures.py, docs/PARAMETERS.md, docs/VERIFICATION.md, .claude/rules/ui-reader.md
added: 2026-11-22
payoff: a contributor looking for the 1 MAC line or the volumes with no supported range finds each under a heading that names it
---

**Problem.** Rename two docs/INTERFACE.md headings that code comments and a test cite: § "What is not bounded this way" covers only the two volumes, and § "MAC-awake as a chart reference" also holds the 1 MAC line

**Found 2026-11-22 by `PL-1VXY`**, which applied the chapter reads of the old
`docs/MODEL.md` (cfb15a4a). Two of their heading proposals were not applied,
because each heading is cited from code comments, and that branch was told not
to re-point code comments while another branch edited them.

1. Chapter read 54 proposes renaming § "What is not bounded this way". Its
   "this way" depends on the heading above it, and the section is now about
   the circuit and alveolar gas volumes only. The read suggests "The circuit
   and alveolar gas volumes have no supported range".
2. Chapter read 63 proposes renaming § "MAC-awake as a chart reference",
   because the section also sets the 1 MAC line. The read suggests "MAC-awake
   and 1 MAC as chart references".

**Citations to update in the same commit** (from a search of the tree on
2026-11-22): `docs/INTERFACE.md` itself, `docs/PARAMETERS.md`,
`docs/VERIFICATION.md`, `.claude/rules/ui-reader.md`,
`src/anesthesia_sim/app/controller.py`, `src/anesthesia_sim/app/theme.py`,
and `tests/reference/test_mac_awake_washout_figures.py`, whose
`SECTION_HEADING` finds the section by its heading text. `ROADMAP.md`, the
release notes and `docs/prose-review/model-reverse-outline.tsv` quote the old
names as history and stay as they are.

**Why it matters.** A heading that does not name what it holds sends a
contributor looking for the 1 MAC line, or for the volumes' missing range, to
the wrong place.

**Done when.** Both headings are renamed and a search of the tree finds no
live citation of either old name.

**Reproduced 2026-11-23.** `docs/INTERFACE.md` still has both old headings.

**Generator check.** A one-off: two headings left unrenamed by `PL-1VXY` because another branch was editing the comments that cite them.
