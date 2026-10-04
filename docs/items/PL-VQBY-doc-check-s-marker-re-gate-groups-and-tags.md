---
id: PL-VQBY
title: doc_check's MARKER_RE, _gate_groups and _tags_region take a bold or emphasis run at the start of a physical line for the start of a statement, so a run opening a soft-break continuation line reads as a section title, a gate group heading or the Tags region; 68 such titles live, no wrong verdict today
status: untriaged
feature: one-answer
touches: tools/doc_check.py, tests/unit
added: 2026-10-04
---

**Problem.** doc_check's MARKER_RE, _gate_groups and _tags_region take a bold or emphasis run at the start of a physical line for the start of a statement, so a run opening a soft-break continuation line reads as a section title, a gate group heading or the Tags region; 68 such titles live, no wrong verdict today

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

CommonMark § 6.7: a continuation line starts no block, so a bold run there is emphasis in the middle of a paragraph. `roadmap.statement_lines` gives each statement's first line.

- `MARKER_RE`, through `_headings`: "...GitHub renders it from the" over "**Cite this repository** button in the sidebar." answers `§ "Cite this repository"` and a `#cite-this-repository` anchor, where the same paragraph reflowed is refused.
- `_gate_groups`: a gate paragraph wrapping "...what the next sentence wraps" onto "*after* the freeze - two entries were added later - is not a heading." reads as a group heading counting 2 of 3 entries, and `check_gate_counts` raises two false errors.
- `_tags_region`: a paragraph's second line "**Tags.** opens on purpose." opens the region there, and the untagged claim under the real `**Tags.**` reads empty.

Live in form: 68 of the 1,884 titles `_headings` returns open a continuation line (`README.md`:237, `docs/MODEL.md`:78), and `ROADMAP.md`:963 and :2542 are continuation lines inside gate subsections; no citation, anchor, count or tag claim rests on one today. `PL-R417`'s first slice fixed a title wrapped *inside* its run; this is the run opening a wrapped line.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
