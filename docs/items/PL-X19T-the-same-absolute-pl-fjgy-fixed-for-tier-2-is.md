---
id: PL-X19T
title: The same absolute PL-FJGY fixed for tier 2 is still stated for tier 3 in expert-review.md, sources-and-docstrings.md and consultant-brief.md, and De Wolf et al. is adopted
priority: P2
effort: S
status: done
classes: defect, docs
feature: worker-instructions
touches: .claude/rules/expert-review.md, .claude/rules/sources-and-docstrings.md, docs/consultant-brief.md, docs/resident-instructions.md
added: 2026-09-07
closed: 2026-09-07
verify: python3 tools/doc_check.py check && ! grep -rqF 'never the authority for a constant' .claude/rules docs/consultant-brief.md
---

**Problem.** The same absolute PL-FJGY fixed for tier 2 is still stated for tier 3 in expert-review.md, sources-and-docstrings.md and consultant-brief.md, and De Wolf et al. is adopted

**Where it is stated.** Three places, and the wording is nearly identical in
each:

- `.claude/rules/expert-review.md:79` — "A **reference implementation is never
  the authority for a constant**, and saying so in a reply is the same error as
  writing it into a file".
- `.claude/rules/sources-and-docstrings.md:26` — "It is never the authority for
  a constant, and neither is a paper whose table simply reprints its parameter
  set".
- `docs/consultant-brief.md:89` — "A reference implementation is never the
  authority for a constant."

**What contradicts them.** All twelve partition coefficients in the three agent
files, and ten of the reference patient's eleven physiologic parameters, are
adopted from tier-3 sources — since `PL-1JDD` those entries carry
`"tier": "reference-implementation", "adopted": true` as declared data rather
than as prose a reader has to infer. `docs/MODEL.md` § "Source hierarchy"
records the same thing in words: of the rows in the provenance table, most are
tier 3.

**Why this is the wider case, not a second instance of the same size.**
`PL-FJGY` fixed a rule stated twice in one document about a tier this project
adopts once. This one is stated in a **resident** rule — `expert-review.md`
loads at launch in every session, before anything has been read — about the
tier this project adopts almost everywhere. A session that takes it literally
concludes the shipped parameter set is inadmissible, which is the opposite of
what the project decided on 2026-09-03 (`PL-D6LX`) and disclosed.

**These sentences are not simply wrong, which is what makes the fix delicate.**
Each continues into the discipline that makes a tier-3 adoption honest —
`sources-and-docstrings.md` immediately adds "Where a stored value is one of
theirs, say so, name what the primary literature reports instead, and give the
difference", which is precisely `docs/MODEL.md`'s new rule. So the letter is an
absolute and the spirit is "never a *silent* authority". Recommend aligning the
letter with the spirit, in the same words the new block uses, rather than
softening the paragraph — the point it is making about a reply that answers
"where does this constant come from?" with "Gas Man" is exactly right and must
survive.

**Editing `expert-review.md` costs a cache invalidation** in whatever session
does it, per `CLAUDE.md`'s note on editing resident files mid-session, so this
wants its own session rather than riding another item's branch.

**Found.** `PL-FJGY` (fix the tier-2 wording), 2026-09-07, in its close-out
sweep. Not fixed there: all three files are outside that item's `touches`, and
two of them are resident instructions.

**Fixed 2026-09-07.** All three sentences now separate the two claims the
absolute had welded together: a reference implementation **measured nothing**,
which is true and is the whole of what the tier means, and whether one may be
*adopted* as the authority for a constant, which `docs/MODEL.md` § "Source
hierarchy" decides and which this project answers yes to for most of what it
stores. The half worth keeping is kept verbatim in each: a reply that answers
"where did this constant come from?" with "Gas Man" is still the same error as
writing it into a file.

- `.claude/rules/expert-review.md` — the resident paragraph. It now names the
  `tier` and `adopted` fields under `src/anesthesia_sim/data/` as what says
  which values rest on an adoption, so a session checks the entry instead of
  applying a rule of thumb, and says in terms that a reply ruling the practice
  out in general is wrong about the shipped set. No count is stated: a number
  in a resident file is a second copy of a fact the data already carries, and
  `ROADMAP.md`'s planned-milestone item 31 would falsify one.
- `.claude/rules/sources-and-docstrings.md` — the full statement, path-scoped
  to the files where a constant lives. It adds what the two adoptions actually
  are, since a session writing a provenance note needs the worked examples:
  the twelve partition coefficients kept over the primary measurements cited
  beside them on the owner's 2026-09-03 decision (`PL-D6LX`), and ten of the
  reference patient's eleven parameters taken from the Gas Man Workbook for
  want of a primary source any session can reach. Those are the two different
  grounds, and the note a session has to write differs between them.
- `docs/consultant-brief.md` — the sentence binds the consultant's own
  evidence, so it keeps that force and drops the false absolute. A reviewer
  reading the old line would have found the adopted tier-3 set and reported a
  contradiction, which is a spent finding: the brief now says the adoption is
  disclosed and on the record, and that whether it was the right call is fair
  game. Both halves matter — foreclosing the scientific objection would be
  worse than the false finding.
- `docs/resident-instructions.md` — the correction and its +450 characters
  recorded under the block's existing entry, with the routing argument
  untouched. Deleting the paragraph to pay for the growth was refused: it is
  resident because it fires in a reply, which no read precedes.

**Departed from this item's own recommendation, deliberately.** The brief
above recommends aligning the letter with the spirit "in the same words the
new block uses". Those words could not be reused. `docs/MODEL.md`'s new block
says a lower tier may be adopted only where "no primary measurement of *this
quantity, in this population* exists or is reachable — never that finding one
is work", and that where a primary is available but unadopted "the value stays
unsourced, which is what all twelve partition coefficients do". Both are
contradicted by the three agent files, where De Wolf et al. is
`"adopted": true` and its note says it "is the source of the stored values",
over primary measurements that are cited, reachable and quantified against.
Copying that wording would have carried `PL-FJGY`'s own defect one file
further. `PL-J302` carries the MODEL.md half; these three files point at the
section rather than restating its conditions, so they stay true whichever way
it is resolved.

**Verified.** `make check` green — 2211 tests, `core/` coverage 100%,
`doc_check` 0 errors and `docket check` 0 errors, the one advisory being the
resident-growth question answered above. The `verify:` command failed before
the work (exit 1, the absolute present in all three files) and passes after.

