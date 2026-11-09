---
id: PL-R3J6
title: docs/MODEL.md gives the full citation for Yasuda 1991, Hendrickx and De Wolf, Targ 1989 and Lerou and Booij in several sections; give each one full citation and a short form elsewhere, in the line edit that follows PL-F0Q2
priority: P3
effort: S
status: ready
classes: docs
feature: model-md-structure
touches: docs/MODEL.md
added: 2026-11-07
payoff: each source has one full citation carrying its reading record, so a reader checking a value never has to compare two copies to find the complete one
verify: ! grep -qE '^  doi:10\.1213/00000539-199103000-00007\.$' docs/MODEL.md && ! grep -qE '^  doi:10\.1097/00000542-199103000-00017\.$' docs/MODEL.md
---

**Problem.** docs/MODEL.md gives the full citation for Yasuda 1991, Hendrickx and De Wolf, Targ 1989 and Lerou and Booij in several sections. Give each source one full citation and a short form elsewhere, in the line edit that follows PL-F0Q2.

**Found 2026-11-07 while restructuring `docs/MODEL.md` (`PL-BSMF`, finding 49,
declined there).** Targ 1989 appears as an inline journal locator and PMID in
desflurane's residual and in § "Known limitations". The residual's locator must
stay, because the residual sits in a required-tests subsection, and that
subsection's paragraph check accepts a published source only as a DOI, PMID,
ISBN or journal locator. Lerou and Booij appear with two different reading
records: full text on 2026-09-06 and abstract on 2026-10-25. Yasuda 1991 and
Hendrickx and De Wolf are given in full more than once. Shortening a citation
means rewording it, so the change belongs to the document's line edit. Keep
every reading record and page number.

**Checked 2026-11-09:** On cfd4a4b6 the repeats are still there. `grep -n 'PMID 1994760\|PMID 2001028\|PMID 2764290\|PMID 18175091\|Lerou JG' docs/MODEL.md` finds Yasuda 1991's two papers in full twice: under § "Published wash-in and elimination validation test" and in § "Known limitations", where the second copy adds the reading record. Hendrickx and De Wolf are in full twice: inline in § "Symbols" and in § "Known limitations", where the copy adds the reading record. Targ, Yasuda and Eger 1989 (PMID 2764290) is given as a journal locator three times, in § "Parameter provenance", desflurane's residual and § "Known limitations". Lerou and Booij is a locator in § "Parameter provenance" and a full citation in § "Parameter-recovery test". The line edit this item was to ride, `PL-95SW` (#2049), has closed, so the item now stands on its own.

**Why it matters.** Two full copies of one citation can drift apart, and one already has: the copy in § "Known limitations" records how deeply the paper was read, and the copy in the test section does not. A reader checking a value against its source then has to compare the two to learn which one is complete.

**Done when.** Each of the four sources is cited in full once, at the place that keeps its reading record and page numbers. Every other mention gives the authors and year and points to that place. A required-tests subsection keeps the journal locator or PMID that its paragraph check needs. For Yasuda 1991 this means the bullet list under § "Published wash-in and elimination validation test" gives way to that pointer, and its table rows keep their locators. No reading record or page number is lost.

**Generator check.** One-off: a finding from the `docs/MODEL.md` restructure (`PL-BSMF`, finding 49), declined there because shortening a citation is rewording. No head's `misread:` states that fact.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Present. At 817a4d88, `docs/MODEL.md` already gave both Yasuda 1991 papers in full twice (PMIDs 1994760 and 2001028) and Hendrickx and De Wolf in full twice. The item is classed `docs` only, which is not debt, so v0.7.0's gate does not take it: it stays off the frozen list and needs no deferral.
