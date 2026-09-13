---
id: PL-ZP7Z
title: The Workbook attributes the volatile partition coefficients to Yasuda's Anesthesiology abstract and to Abbott package-insert data, which is not what the agent files say
priority: P1
effort: M
status: done
classes: science
feature: model-spec-accuracy
touches: src/anesthesia_sim/data/agents/sevoflurane.json, src/anesthesia_sim/data/agents/isoflurane.json, src/anesthesia_sim/data/agents/desflurane.json, docs/MODEL.md
added: 2026-09-06
closed: 2026-09-13
verify: python3 tools/doc_check.py check && grep -q 'A615' src/anesthesia_sim/data/agents/sevoflurane.json
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

**The `verify:` command anchors on the abstract's own citation.** The Done-when
requires the files to record which edition of Yasuda is at issue, and the
Workbook's reference 45 is `Anesthesiology 69:A615` rather than the 1989
`Anesthesia & Analgesia` paper the agent files cite, so recording the
distinction necessarily names it. Run 2026-09-06 before the work: exit 1, with
`doc_check` passing and `A615` absent from all three agent files.


**Closed 2026-09-13. The tier does not change, and the reasoning is recorded in
all three agent files.** Each Yasuda entry now says what the Workbook
attributes, in the Workbook's own words; that its reference 45 is the abstract
`Anesthesiology 69:A615` from the 1988 ASA annual-meeting supplement rather
than the 1989 *Anesthesia & Analgesia* paper the files cite, and that a PubMed
search returns nothing for it, as a meeting-abstract supplement does; and that
Anesthesiology volume 69 (1988) and Anesth Analg volume 69 (1989) collide by
coincidence, so "Yasuda 69" identifies neither.

**The arithmetic, which is new and is what makes the attribution answerable at
all.** Yasuda's measured brain:blood times each file's stored blood:gas
reproduces sevoflurane's and desflurane's stored vessel-rich tissue:gas exactly
(1.70 x 0.65 = 1.1050 -> 1.1; 1.29 x 0.42 = 0.5418 -> 0.54) and misses
isoflurane's (1.57 x 1.3 = 2.0410 against a stored 2.1) by 2.9 percent, which
is inside half that measurement's own SD. Close enough to suggest the route,
never enough to name it. This also explains something `sevoflurane.json`
already recorded without an explanation - the half-percent agreement that had
read as a near-coincidence.

**The tier stays reference-implementation, adopted, on three grounds**, the
first sufficient alone: a program's statement about its own provenance is the
program talking, which is the same rule that stops De Wolf's journal name from
promoting the table it prints; the Workbook's own paragraph contradicts itself
for sevoflurane, crediting it to Yasuda and then to the package insert and
Abbott data; and whatever it took, it took at an unstated rounding through a
blood:gas that sentence attributes to nobody.

**The gap this leaves, recorded rather than inferred across** (`PL-B9K7`). The
stored coefficients are tissue:gas and the 1989 abstract reports tissue:blood
only, which is why the comparison has to pass through that blood:gas. The full
paper reports both: Yasuda et al. 1991 (*Anesth Analg* 1991;72:316-24, PMID
1994760), read at full text from the private reference corpus 2026-09-13, cites
it for "the tissue/blood partition coefficient (which we determined
previously)" and for "the tissue/gas partition coefficient" in one methods
paragraph. That paper is not in PubMed Central and not among the corpus's
holdings, so the route ends there. Reading it would settle this outright.
