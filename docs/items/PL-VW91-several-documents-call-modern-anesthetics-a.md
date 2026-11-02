---
id: PL-VW91
title: Several documents call Modern Anesthetics, a textbook, tier 3, where docs/MODEL.md § Source hierarchy defines a review or textbook as tier 2: .claude/rules/citing-sources.md ('Both remain tier 3') and the private corpus README's Holdings paragraph
priority: P3
effort: S
status: done
classes: docs
feature: stale-source-claims
milestone: v0.6.14
touches: .claude/rules/citing-sources.md, docs/references/README.md, docs/MODEL.md
added: 2026-10-25
closed: 2026-11-02
pr: 1940
payoff: the citing rule gives a textbook the tier docs/MODEL.md gives it, so a session weighs Modern Anesthetics as a secondary synthesis
verify: ! grep -qF 'Both remain tier 3' .claude/rules/citing-sources.md
---

**Problem.** Several documents call Modern Anesthetics, a textbook, tier 3, where docs/MODEL.md § Source hierarchy defines a review or textbook as tier 2: .claude/rules/citing-sources.md ('Both remain tier 3') and the private corpus README's Holdings paragraph

**Reproduced 2026-10-26.** `docs/MODEL.md` § "Source hierarchy" defines tier 2
as "A review, textbook, monograph or consensus document". In
`.claude/rules/citing-sources.md`, the paragraph on the two whole textbooks
says "Both remain tier 3". That is correct for the Gas Man Workbook, which
`docs/MODEL.md` treats as tier 3, but not for *Modern Anesthetics*. The
sentence was written on 2026-09-15 (`PL-9GP1`), after the tiers were defined on
2026-09-02, so it was wrong when written. `docs/references/README.md` also
calls a review "tier 3" where it introduces the Eger and Saidman 2005 review cited beside
Yasuda 1991. Whether that line breaks the same definition is for the fix to
decide. The corpus README is in the separate references repository, so it is
not among this item's `touches`.

**Why it matters.** The tier decides whether a source may be the authority for
a stored value. A session that follows the rule file treats a textbook as a
reference implementation, which `docs/MODEL.md` says "is still not a source".

**Done when.** `.claude/rules/citing-sources.md` gives *Modern Anesthetics*
tier 2 and the Workbook tier 3. The review line in `docs/references/README.md`
agrees with `docs/MODEL.md` or says why it differs. The corpus README's
Holdings paragraph is corrected in its own repository.

**Generator check.** The misread fact is the tier that `docs/MODEL.md` §
"Source hierarchy" gives a textbook. No head's `misread:` line names source
tiers, so it is a one-off.

**The corpus half, 2026-11-02.** The references repository's README called two
secondary syntheses tier 3: the Holdings paragraph's "a book chapter is a
review, tier 3", and the Eger and Saidman 2005 entry. Both now say tier 2, and
the Holdings paragraph adds that the Gas Man Workbook is tier 3. The change is
`stuthedew/open-anesthesia-sim-references` pull request 1, commit `a582658`,
which touches `README.md` alone. A session cannot merge it: that repository's
`main` has no protection that binds an admin, so the merge hook leaves the
Squash and merge to the owner. The entry on Gas Man's parameter set, which
calls that set tier 3, is correct and unchanged.

**Closed 2026-11-02.** `.claude/rules/citing-sources.md` gives *Modern
Anesthetics* tier 2 and the Gas Man Workbook tier 3. `docs/references/README.md`
and `docs/MODEL.md`'s reference list both give the Eger and Saidman 2005 review
tier 2. Blind review found that `docs/MODEL.md`'s entry had ranked it tier 3
for its disclaimer that its figures are illustrative. That disclaimer is a
reason for caution, not a tier, so the entry keeps it as a caution. The corpus
half is the references pull request above, waiting on the owner's merge.
