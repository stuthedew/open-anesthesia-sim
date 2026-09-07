---
id: PL-X19T
title: The same absolute PL-FJGY fixed for tier 2 is still stated for tier 3 in expert-review.md, sources-and-docstrings.md and consultant-brief.md, and De Wolf et al. is adopted
status: untriaged
added: 2026-09-07
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

