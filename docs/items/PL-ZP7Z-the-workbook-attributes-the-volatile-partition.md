---
id: PL-ZP7Z
title: The Workbook attributes the volatile partition coefficients to Yasuda's Anesthesiology abstract and to Abbott package-insert data, which is not what the agent files say
status: untriaged
added: 2026-09-06
---

**Problem.** The three agent files under `src/anesthesia_sim/data/agents/`
record their partition coefficients as tier 3, sourced from De Wolf et al.
2012's Table 1, with Yasuda, Targ and Eger cited alongside and explicitly *not
adopted*. The Gas Man Workbook, read at the source 2026-09-06 (Appendix B, page
168, copy supplied by the project owner), says something different about the
same numbers. The notes under its Model Parameters table read:

> Values for nitrous oxide and enflurane are taken from Eger, 1981. Values for
> isoflurane, halothane, desflurane and sevoflurane are taken from Yasuda, Targ
> and Eger. Values for nitrogen are taken from Weathersby and Homer, 1980.
> Values for sevoflurane are taken from the package insert and Abbott data.

Two things follow, and they pull in opposite directions.

**First, Gas Man says its volatile coefficients ARE Yasuda's** - so the agent
files' framing, that Yasuda is a primary measurement cited but not adopted
while the stored value came from somewhere else, may understate the
relationship. The stored sevoflurane tissue:blood values already sit within
half a percent of Yasuda's, which `sevoflurane.json` records as a near match
without an explanation; this would be the explanation.

**Second, the Workbook's own attribution is self-contradicting for
sevoflurane** - the same paragraph credits it to Yasuda and, one sentence
later, to the package insert and Abbott data. And its reference 45 is the
*abstract*, `Anesthesiology 69:A615`, not the 1989 *Anesthesia & Analgesia*
paper the agent files cite. An abstract and a full paper are not
interchangeable sources.

**Why it matters.** `docs/MODEL.md` § "Source hierarchy" turns on the
difference between a value that descends from a measurement and one that
descends from a parameter set, and this is direct evidence about which the
twelve coefficients are. It does not obviously promote them - a program's claim
about its own provenance is still the program talking - but it is the kind of
evidence the tier assignment should be made against rather than around.

**Where.**

- `src/anesthesia_sim/data/agents/sevoflurane.json`, `isoflurane.json`,
  `desflurane.json` - the De Wolf and Yasuda `sources` notes.
- `docs/MODEL.md` § "Parameter provenance", the paragraph on the shared source
  table and what tier 3 means for it.

**Related.** `PL-D6LX` (decide whether to adopt primary-literature partition
coefficients) is closed on the reasoning that the stored set is Gas Man's and
Yasuda was not adopted. This is new evidence bearing on that decision rather
than a defect in it; whether it reopens the question is the judgment this item
carries.

**Done when.** The agent files' Yasuda notes say what the Workbook attributes,
which edition of Yasuda is at issue, and whether the tier assignment changes -
or record that it does not, with the reasoning.
