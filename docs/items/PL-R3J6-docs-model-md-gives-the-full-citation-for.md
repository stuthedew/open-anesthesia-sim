---
id: PL-R3J6
title: docs/MODEL.md gives the full citation for Yasuda 1991, Hendrickx and De Wolf, Targ 1989 and Lerou and Booij in several sections; give each one full citation and a short form elsewhere, in the line edit that follows PL-F0Q2
priority: P3
effort: S
status: done
classes: docs
feature: model-md-structure
touches: docs/MODEL.md, docs/VERIFICATION.md
added: 2026-11-07
closed: 2026-11-22
payoff: each source has one full citation carrying its reading record, so a reader checking a value never has to compare two copies to find the complete one
verify: grep -qF 'with a record of what was read in each' docs/VERIFICATION.md
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

**Checked 2026-11-22** against `d4e8200`: still applies. `grep -n "PMID 1994760\|PMID 2001028\|Special aspects\|218–25" docs/MODEL.md` still finds both Yasuda 1991 papers in full twice, under § "Published wash-in and elimination validation test" and in § "Known limitations". It finds Hendrickx and De Wolf in full twice, in § "Symbols" and § "Known limitations", and Targ 1989 as a journal locator three times. Lerou and Booij is still a locator in one section and a full citation in another.

**Built 2026-11-22**, on a branch that carries `PL-48MX` (the clinician's `docs/MODEL.md`) and the sorting of the other three documents by reader. `grep -n -E 'PMID 1994760|PMID 2001028|00000539-199103000-00007|00000542-199103000-00017|Special aspects|PMID 2764290|18175091|11575385|Lerou|Hendrickx|Targ' docs/MODEL.md docs/VERIFICATION.md docs/PARAMETERS.md docs/INTERFACE.md README.md` showed where each source now stands.

1. In `docs/MODEL.md` the problem is gone. `PL-48MX` gave it one § "References" list, which gives Yasuda et al. 1991a and 1991b, Hendrickx and De Wolf 2008 and Targ 1989 once each, and the text cites them by authors and year. `docs/MODEL.md` no longer cites Lerou and Booij.
2. The other copies moved with their sections. The test sections went to `docs/VERIFICATION.md`, and the evidence behind the limitations, with its reading records, went to `docs/PARAMETERS.md`. So `docs/VERIFICATION.md` still gave the two Yasuda papers in full without a reading record, Hendrickx and De Wolf in full inline, and Lerou and Booij in full with only the 2026-10-25 abstract record.
3. The repository's list of sources with their reading records is `docs/references/README.md` § "The documents". It has entries for both Yasuda papers, for Hendrickx and De Wolf (under the *Modern Anesthetics* volume) and for Targ 1989, and none for Lerou and Booij.

What changed, all in `docs/VERIFICATION.md`:

1. In § "Published wash-in and elimination validation test", the bullet list of the two Yasuda papers gave way to a pointer to `docs/references/README.md` § "Yasuda et al. 1991 — the two human kinetics papers". The table rows keep their journal locators, and the sentence recording that the figures were read from the abstracts and checked against PubMed on 2026-09-06 stays.
2. In § "Symbols", the inline full citation of Hendrickx and De Wolf gave way to "(2008, pp. 161-162)" and a pointer to `docs/references/README.md` § "Schüttler & Schwilden 2008 — *Modern Anesthetics*". The same section already points there for Baker and Farmery. Every page number stays.
3. In § "Parameter-recovery test", Lerou and Booij's full citation stays, because it is the only one in the four documents and the required-tests check needs its locator. Its reading record now gives both readings: full text on 2026-09-06 (`PL-8ZJQ`) and the abstract through PubMed on 2026-10-25 (`PL-4L6Z`).
4. Targ 1989's journal locator in desflurane's residual stays, as the done condition says.

Left as they were, and why:

1. `docs/MODEL.md` § "References" keeps its full entries, because `PL-48MX` gave the clinician's document its own reference list.
2. `docs/PARAMETERS.md` § "Intertissue diffusion: the missing fourth compartment" ends with a source list that gives both Yasuda papers and Hendrickx and De Wolf in full, with reading records that repeat part of `docs/references/README.md`'s entries. Each section of that document ends with its own source list, which `PL-N83Z` kept, and the document is outside this item's `touches`. Whether those lists should point to `docs/references/README.md` instead is a question for its own item. Its mentions of Lerou and Booij and of Targ 1989 are journal locators.
3. The docstring of `tests/reference/test_parameter_recovery.py` repeats Lerou and Booij's citation with only the abstract record. A test docstring is outside a documentation item.

One finding, not fixed here: `docs/references/README.md` records reading pp. 163, 165 and 166 of Hendrickx and De Wolf's chapter, but not pp. 161-162, 167, 169 and 171, which `docs/VERIFICATION.md` § "Symbols" and `docs/MODEL.md` § "Units and symbols" cite for the symbols. It was reported for filing.

**Documents checked.** `docs/MODEL.md` § "References", § "Units and symbols" and every short-form mention the search found; `docs/VERIFICATION.md` § "Published wash-in and elimination validation test", § "Desflurane's residual, and why the parameter file was not changed", § "The early wash-in curve against the published figures", § "Parameter-recovery test" and § "Symbols"; `docs/PARAMETERS.md` (the mentions listed above); `docs/references/README.md` (the three entries); `docs/INTERFACE.md` and `README.md` (none of the four sources).
