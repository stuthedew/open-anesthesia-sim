---
id: PL-J302
title: docs/MODEL.md's new lower-tier block admits an adoption only where no primary is reachable, and says the twelve partition coefficients stay unsourced, but the three agent files declare De Wolf et al. adopted over cited primaries
priority: P1
effort: S
status: done
classes: science, docs
feature: model-spec-accuracy
milestone: v0.4.10
touches: docs/MODEL.md
added: 2026-09-07
closed: 2026-09-07
pr: 454
verify: python3 tools/doc_check.py check && grep -qF 'carries no adopted primary' docs/MODEL.md && ! grep -qF 'the value stays unsourced' docs/MODEL.md
---

**Problem.** docs/MODEL.md's new lower-tier block admits an adoption only where no primary is reachable, and says the twelve partition coefficients stay unsourced, but the three agent files declare De Wolf et al. adopted over cited primaries

**Decision needed.** Whether `docs/MODEL.md` § "Source hierarchy" names a
second admissible ground for adopting a lower tier — taking a complete,
internally consistent parameter set where the primary literature offers
scattered measurements — or whether the twelve partition coefficients are an
exception the section should name as one. No stored value changes either way.

**The two sentences.** Both are in the block `PL-FJGY` added on 2026-09-07,
in the paragraph that follows its three obligations:

- "The reason has to be that no primary measurement of *this quantity, in this
  population* exists or is reachable — never that finding one is work."
- "Where a primary measurement *is* available and simply has not been adopted,
  the entry says so in those words and the value stays unsourced, which is
  what all twelve partition coefficients do."

**What the data says instead.** `sources[0]` of each of the three agent files
is De Wolf et al. 2012, `"tier": "reference-implementation"`,
`"adopted": true`, with the note "It is the source of the stored values". The
primary measurements are cited in the same files — Eger 1987, Yasuda et al.,
Strum and Eger, Malviya and Lerman, Lerman et al. 1984 — each `adopted: false`
and each recording the measured value and the difference from the stored one
(desflurane −0.9%, sevoflurane −5.2%, isoflurane −11.0%). So a primary
measurement is available, reachable, read and quantified against, and the
tier-3 value was kept anyway, by the project owner's decision of 2026-09-03
(`PL-D6LX`). Neither sentence describes that: the first excludes it, and the
second says the values are unsourced when `adopted` says they are not.

**The ground the block is missing is one the same section already argues.**
Tier 3's own bullet says the tier "supplies a complete, internally consistent
set where the primary literature supplies scattered measurements made in
different laboratories on different cohorts". That is exactly why the twelve
were kept: mixing one laboratory's blood:gas figure into a Gas Man tissue set
makes the trajectory a hybrid of two parameter lineages, which is the same
objection § "Why the Mapleson values are nonetheless not adopted here" makes
against a Mapleson MAC divisor. The block reads as though set coherence were
not a reason at all, and "never that finding one is work" then makes the
project's largest disclosed adoption look like the thing the rule forbids.

**Why this is not merely wording.** `docs/MODEL.md` is the authoritative
specification and this section is what every provenance note in the repository
cites. A session reading it concludes the shipped coefficient set is
inadmissible and either "fixes" a data file or writes a note contradicting the
one beside it — which is the harm `PL-X19T` had just removed from the three
instruction files, arriving back through the document they now point at.

**Recommendation.** Name the second ground and keep the bar high: a lower tier
may be adopted where no primary measurement is reachable, *or* where the value
belongs to a set whose internal consistency is the thing being modelled and
the primaries would have to be mixed across cohorts to replace it — in both
cases with the difference from each cited primary recorded on the entry, which
all twelve already carry. Then replace "the value stays unsourced" with "the
value carries no adopted primary", since `adopted` is a declared field since
`PL-1JDD` and "unsourced" now reads as a claim about it. `ROADMAP.md`'s
planned-milestone item 31 is the route to a primary set and is unaffected.

**Found.** `PL-X19T` (align the tier-3 absolute in the instruction files with
the practice), 2026-09-07. Not fixed there: `docs/MODEL.md` is outside that
item's `touches`, it is `science`-classed work in the authoritative
specification, and the wording is the project owner's call — the tier-2 twin
of this question was decided by them rather than answered by a session.

**Decided 2026-09-07 by the project owner: the recommendation above, both
halves.** Built in the same session, on `PL-X19T`'s branch, since the two are
one finding at two levels and the second was found while writing the first.

The paragraph now names **two** admissible reasons for adopting a lower tier
and says that finding a primary source being work is neither of them:

1. *No primary measurement of this quantity, in this population, exists or is
   reachable.* This is where the whole reference patient sits, including the
   five parameters that carry a primary citation beside them — and working
   through those five is what showed the reason covers more than it appeared
   to. Hudgel and Devadatta measured **awake** functional residual capacity
   where the stored volume is an anaesthetised lung; Cattermole et al.
   measured a different population; Janssen et al. report a muscle **mass**
   where this model holds a volume. Each note already recorded which mismatch
   it was, which is what makes the citation a comparison rather than a source.
2. *The value belongs to a set whose internal consistency is part of what is
   being modelled*, and the reachable primaries would have to be mixed across
   laboratories and cohorts to replace it. This is tier 3's own bullet made
   into a rule, and the twelve partition coefficients are its worked example -
   the only case in the file where the primaries genuinely measured the same
   quantity in the same population and the tier-3 value was kept anyway.

The second reason is bounded rather than open: it is available only where the
primaries are cited on the entry with the measured value and the difference
recorded, so the cost is visible - desflurane -0.9%, sevoflurane -5.2%,
isoflurane -11.0% - and `ROADMAP.md`'s planned-milestone item 31 would retire
it for these twelve. "The value stays unsourced" became "the value **carries
no adopted primary**", which is a claim about the `adopted` field `PL-1JDD`
made machine-readable rather than about the citation.

**The Mapleson passage needed no edit and now agrees.** Its second reason -
that a Mapleson divisor over a Gas Man trajectory makes each displayed
multiple a ratio between two parameter lineages - is reason 2 stated for
`mac_percent`, so the block and the passage argue the same thing from
opposite sides. The block cites it as such.

**No stored value, `tier` or `adopted` flag changed.** The four data files
declare exactly what they declared before; what changed is that the standard
now describes the practice it was written to govern.

**Verified.** `verify:` failed before the work (the phrase did not exist) and
passes after.
