---
id: PL-YYL2
title: ROADMAP item 29 says nine items carry v0.4.1 and names PL-P0BB, which closed in v0.3.2, so eight remain
priority: P3
effort: S
status: done
classes: docs, defect
feature: planning-cadence
milestone: v0.4.1
touches: ROADMAP.md
added: 2026-09-05
closed: 2026-09-05
pr: 356
verify: python3 tools/doc_check.py check && grep -qF 'Corrected 2026-09-05 (`PL-YYL2`)' ROADMAP.md
---

**Problem.** `ROADMAP.md`'s planned-milestone item 29 says "Nine items carry
it: `PL-P0BB`, `PL-GS5X` and `PL-X9KD` under `numerical-domain`, and six under
`core-domain-language`", and the timeline's v0.4.1 row repeats the nine by id.
`PL-P0BB` is `done`, `milestone: v0.3.2`, closed 2026-09-03 (#256). Eight
remain.

**Why it matters.** It is the count a session sizes the release from, in the
two places a session looks. `PL-P0BB` was the state-vector decision that
*authorized* `PL-GS5X`; counting it as outstanding makes the release look like
it still has an open design question at its head when the question is answered
and recorded.

**Also missing from the same two lists, in the other direction.** `PL-VZL0`
names `PL-X2XX` (`ready`) as a prerequisite, and it appears in neither list -
see `PL-GGCN` for why no check reported it.

**Where.** `ROADMAP.md` planned-milestone item 29 ("Nine items carry it"), and
the timeline's `v0.4.1` row.

**Done when.** Both places name the eight open items, and `PL-P0BB` is recorded
as already shipped rather than as outstanding scope.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-M3MV`).** `ROADMAP.md`'s § "Planned milestones" carried this paragraph under item 29, "Make core/ read like the domain". In it, "this item" means item 29, "here" means that entry, "this file" means `ROADMAP.md`, and "above" and "below" point within `ROADMAP.md` as it then stood. Item 29 now says that nine items carry the step and that the `v0.4.x` row of § "The timeline" lists them.

> Nine items carry this step: `PL-GS5X` and `PL-X9KD` under `numerical-domain`, six under `core-domain-language`, and `PL-X2XX`. `PL-VZL0` requires `PL-X2XX`, and `PL-X2XX` went unlisted here until `PL-GGCN` taught the checker to read the second half of a compound prerequisite. `PL-P0BB` was counted as a tenth, and it no longer is. The state-vector decision that it recorded shipped in v0.3.2. Counting it made the step look as though it still had an open design question at its head, when that question is answered. This was corrected on 2026-09-05 (`PL-YYL2`). The timeline row above carries the same list and the same correction.
