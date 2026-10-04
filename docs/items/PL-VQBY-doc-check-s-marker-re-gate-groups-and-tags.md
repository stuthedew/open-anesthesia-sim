---
id: PL-VQBY
title: doc_check's MARKER_RE, _gate_groups and _tags_region take a bold or emphasis run at the start of a physical line for the start of a statement, so a run opening a soft-break continuation line reads as a section title, a gate group heading or the Tags region; 68 such titles live, no wrong verdict today
priority: P3
effort: M
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: a bold run a reflow puts at a line's start is read as the sentence it continues, so no citation, gate count or tags claim rests on a heading the page does not show
verify: grep -qF '"gate groups, ' tests/unit/test_doc_check.py && grep -qF '"tags region, ' tests/unit/test_doc_check.py && grep -qF '"section titles, a bold run opening a continuation line' tests/unit/test_doc_check.py
---

**Problem.** doc_check's MARKER_RE, _gate_groups and _tags_region take a bold or emphasis run at the start of a physical line for the start of a statement, so a run opening a soft-break continuation line reads as a section title, a gate group heading or the Tags region; 68 such titles live, no wrong verdict today

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

CommonMark § 6.7: a continuation line starts no block, so a bold run there is emphasis in the middle of a paragraph. `roadmap.statement_lines` gives each statement's first line.

- `MARKER_RE`, through `_headings`: "...GitHub renders it from the" over "**Cite this repository** button in the sidebar." answers `§ "Cite this repository"` and a `#cite-this-repository` anchor, where the same paragraph reflowed is refused.
- `_gate_groups`: a gate paragraph wrapping "...what the next sentence wraps" onto "*after* the freeze - two entries were added later - is not a heading." reads as a group heading counting 2 of 3 entries, and `check_gate_counts` raises two false errors.
- `_tags_region`: a paragraph's second line "**Tags.** opens on purpose." opens the region there, and the untagged claim under the real `**Tags.**` reads empty.

Live in form: 68 of the 1,884 titles `_headings` returns open a continuation line (`README.md`:237, `docs/MODEL.md`:78), and `ROADMAP.md`:963 and :2542 are continuation lines inside gate subsections; no citation, anchor, count or tag claim rests on one today. `PL-R417`'s first slice fixed a title wrapped *inside* its run; this is the run opening a wrapped line.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `09cdc761`, `doc_check._headings` over "GitHub renders it from the" above "**Cite this repository** button in the sidebar." returns `['Cite this repository']`, one sentence read as a section title.

**Why it matters.** Section citations and anchors are held to `_headings`, gate counts to `_gate_groups` and the untagged-versions claim to `_tags_region`, so a bold run a reflow puts at a line's start answers a citation naming no section, splits a gate's count, or moves the Tags region, each a verdict on text the page renders as one sentence.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** `MARKER_RE`, `_gate_groups` and `_tags_region` take a bold or emphasis run for a title, a group heading or the Tags mark only where it opens a statement as `statement_lines` gives it, so one opening a soft-break continuation line is read as the paragraph's own text; `section titles, ...`, `gate groups, ...` and `tags region, ...` cases in `CONTINUED_STATEMENTS` pin it.
