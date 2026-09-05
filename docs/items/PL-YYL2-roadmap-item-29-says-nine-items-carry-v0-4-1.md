---
id: PL-YYL2
title: ROADMAP item 29 says nine items carry v0.4.1 and names PL-P0BB, which closed in v0.3.2, so eight remain
status: untriaged
added: 2026-09-05
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
