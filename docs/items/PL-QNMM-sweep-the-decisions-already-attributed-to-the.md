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

**What `PL-7RYB` settled on 2026-09-20, and what is left here.** `CLAUDE.md`'s
`Record which it was` bullet now reads the *date* rather than the absence: a
plain `(project owner, DATE)` dated before 2026-09-16 records no kind at all,
is read as unrecorded rather than as specified, and is reopened on ordinary
evidence while saying the kind is unrecorded. That was one clause against
sweeping, and it changes this item's job rather than doing it. All 234
attributions in the tree stop reading as the opposite of what they are, so the
sweep is no longer what makes the record *honest*; it is what makes the 52
load-bearing ones in `ROADMAP.md` and `docs/MODEL.md` - the decisions a later
session cites to refuse work - say which kind they were instead of saying
nothing. Worth doing, and no longer urgent: `P3` is right.

**Two consequences for the pass itself.** The `Done when` above asks for the
undecidable ones to be *listed*; under the reading rule they need no list,
because leaving one untouched now says "unrecorded" in the same words the rule
does. The opposite case is the one that gained a problem: a pre-2026-09-16
decision this sweep reads as plainly **specified** can no longer be recorded by
leaving it alone, since leaving it alone is now the unrecorded form. Write that
one `(project owner, DATE, specified)` - this session's recommendation, and the
only place in the tree the third token is needed, which is why it is recorded
here and not in `CLAUDE.md`. The `swept for ratified-versus-specified` line
this item's `verify:` already requires is what tells a later session that
`ROADMAP.md`'s plain markers have been read and mean what they say.
