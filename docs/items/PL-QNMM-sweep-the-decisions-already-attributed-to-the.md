---
id: PL-QNMM
title: Sweep the decisions already attributed to the project owner and mark which were ratified recommendations rather than specified behavior, since the distinction was only introduced on 2026-09-16
status: ready
added: 2026-09-16
priority: P3
effort: M
classes: docs
touches: ROADMAP.md, docs/MODEL.md, docs/items
verify: python3 tools/doc_check.py check && grep -qF 'swept for ratified-versus-specified' ROADMAP.md
---

**Problem.** Sweep the decisions already attributed to the project owner and mark which were ratified recommendations rather than specified behavior, since the distinction was only introduced on 2026-09-16

**Why it matters.** `PL-XWH4` introduced the distinction on 2026-09-16 and
marked only that session's own decisions. Everything attributed before it reads
`(project owner, DATE)` whichever kind it was, so the convention is only half
true across the tree - and the half that is missing is the one that would let a
session reopen a recommendation it made itself. The owner's own words: "There
have been multiple items like that."

**The bar is honesty, not completeness.** Where the record does not say and the
session cannot tell, it stays as it is rather than being guessed at: a wrongly
firm attribution is what this is fixing, and a wrongly soft one is the same
error in the other direction. `ROADMAP.md`'s big decisions are where it pays -
the ones a later session would cite to refuse work.

**Done when.** The decisions attributed to the project owner in `ROADMAP.md`
and `docs/MODEL.md` have been read against their own recorded context, the ones
that were plainly recommendations agreed to are marked `ratified` with what each
was chosen over, the ones that were plainly specified are left as they are, and
the ones that cannot be told apart are listed rather than guessed. `ROADMAP.md`
records that the sweep happened and on what date.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation). Still real, and here is the
population it never counted.** Over `\(project owner[^)]*\)`: `ROADMAP.md` holds
81 attributions of which 20 carry `ratified`, leaving **47 unmarked and dated
before 2026-09-16**; `docs/MODEL.md` holds 9 of which 2 carry `ratified`,
leaving **5**. **52 outstanding in total.** Every `ratified` mark in either file
is dated 2026-09-16 or later, so nothing predating `PL-XWH4`'s rule has been
swept, and `grep -qF 'swept for ratified-versus-specified' ROADMAP.md` finds
nothing. The conversions that have happened (`PL-1YT5`, `PL-YTDN`, `PL-ZMGR`)
are one at a time and outside these two files. `PL-7RYB` is the same question
for closed items and is still `needs-decision`.
