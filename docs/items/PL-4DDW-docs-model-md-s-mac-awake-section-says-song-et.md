---
id: PL-4DDW
title: docs/MODEL.md's MAC-awake section says Song et al.'s 2.17% corroborates desflurane's 2.16% band centre without saying that Song's standard deviation of 0.25% leaves the comparison blind to an error of less than about 11% in the stored fraction
priority: P3
effort: S
status: ready
classes: docs
touches: docs/MODEL.md
added: 2026-10-17
payoff: the MAC-awake section says how much the Song comparison can see, so a reader does not take a two-digit agreement for a tight validation
verify: grep -q '0.25%' docs/MODEL.md
---

**Problem.** docs/MODEL.md's MAC-awake section says Song et al.'s 2.17% corroborates desflurane's 2.16% band centre without saying that Song's standard deviation of 0.25% leaves the comparison blind to an error of less than about 11% in the stored fraction

**Evidence.** `docs/MODEL.md` § "MAC-awake as a chart reference" says the
stored fraction "corroborates independently for desflurane: 0.36 of the
stored 6.0% is 2.16%, against the 2.17% Song et al. measured in the
non-jaundiced control arm". Song et al. 2005's abstract (PMID 15731594, read
through PubMed on 2026-10-17) gives that arm as "2.17 +/- 0.25%" (mean +/-
SD) and gives no group size. A centre within one of Song's standard
deviations of 2.17% admits any fraction from 0.320 to 0.403 of MAC, which is
about 11% below to 12% above the stored 0.36. `PL-H1JH` rewrote the test of
this comparison to use Song's standard deviation and to say so in its
docstring. The sentence in `docs/MODEL.md` still reads as agreement to a
hundredth of a percent.

**Why it matters.** `docs/MODEL.md` is the specification a reader trusts. A
two-digit agreement with a population mean whose spread is 25 times wider
implies a validation far tighter than the comparison supports, which the
safety-critical standard asks the project not to imply.

**Done when.** The sentence states Song's standard deviation, or the size of
error the comparison can detect, beside the 2.17%.
