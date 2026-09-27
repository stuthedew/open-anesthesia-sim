---
id: PL-FBY3
title: docs/MODEL.md's intertissue-diffusion note records Eger and Saidman 2005 as abstract-only, though the private corpus now holds its full text, which confirms the note and adds a bias it does not name: the lean tissues that lose agent to fat equilibrate more slowly than a perfusion-limited group, the brain excepted
status: untriaged
feature: model-spec-accuracy
touches: docs/MODEL.md, docs/references/README.md
added: 2026-09-27
---

**Problem.** docs/MODEL.md's intertissue-diffusion note records Eger and Saidman 2005 as abstract-only, though the private corpus now holds its full text, which confirms the note and adds a bias it does not name: the lean tissues that lose agent to fat equilibrate more slowly than a perfusion-limited group, the brain excepted

Found 2026-09-27 reviewing the full text the project owner supplied, now in the
private corpus (`stuthedew/open-anesthesia-sim-references` commit `388ad32`,
README.md § "Eger & Saidman 2005", with every printed page recovered in its
text dump). `PL-WMCJ`'s note in `docs/MODEL.md` § "Known limitations" ("Fat
fills here only through its own blood supply…") was built from the two Yasuda
1991 papers and lists Eger and Saidman as abstract-only. What it now owes:

1. **Route and depth.** Its sources list says the full text was not read. Read
   at full text, pp. 1020–33; tier 3, since PubMed types it "Review" and the
   paper says its figures are "not necessarily precise (quantitative)" (p. 1020).
2. **Corroboration, and its limit.** Table 3 (p. 1024) draws intertissue
   diffusion as a fourth group, "a subset of the FG": 2.9 L of a 14.5 L fat
   group, an effective 12.6 mL/min per 100 mL, τ 230, 412 and 396 min
   (desflurane, sevoflurane, isoflurane) against bulk fat's 1226, 2198 and 2114.
   These cite the Yasuda papers and sit within 1 SD of the fits' fourth and
   fifth compartments in all four cohorts. P. 1025: elimination studies
   "indicate that intertissue diffusion accounts for approximately 30% of the
   anesthetic taken up (3–7)". Refs 3–7 are Carpenter 1986–87 and Yasuda 1991,
   all Eger's group, so the note's "Two cautions" should say this restates the
   interpretation rather than confirming it independently.
3. **A bias the note does not name.** P. 1025: part of the intestine, liver,
   kidney and heart, and part of the muscle/skin, "are slower to reach
   equilibrium because anesthetic is continuously lost to adjacent fat"; at
   50 min of desflurane the muscle group "would reach 74%" of what reaches it
   "[w]ere it not for losses by intertissue diffusion" (p. 1025). On that
   reading the model's muscle and non-brain vessel-rich traces run high, and
   its uptake low. The brain is exempt and drawn apart for that reason
   (p. 1022), so intertissue loss drawn from a vessel-rich group that also
   stands for the brain would slow the brain too — check which trace the
   effect site reads, and record it for whoever builds the route.
4. **Emergence at full text.** Cite p. 1032's "might not influence emergence
   materially" rather than the abstract.

`docs/references/README.md` owes the extraction note for the corpus reading.
Recommendation: do all four in one pass, as `PL-WMCJ` did; no stored value,
code or test changes.

**Added 2026-09-27: *Modern Anesthetics* ch 8 corroborates the description,
not the evidence.** Hendrickx & De Wolf (Handb Exp Pharmacol 2008;182:159–86,
PMID 18175091, in the private corpus) restate Eger's five-compartment model — a
lung and an "intertissue diffusion" compartment added (Carpenter et al. 1986),
"hypothesized to be fat adjacent to well-perfused tissues" (p. 163) — and
Yasuda's fourth compartment "interpreted as" intertissue diffusion (p. 166,
Fig. 3). Every source they cite for it is Eger's group, Eger & Saidman 2005
included, and their text gives no volume, time constant or share of uptake, so
it adds no independent evidence. What it adds is the other side, which the
note's "Two cautions" carries only as Hull:

- Ishibashi et al. 2006 (*Anesthesiology* 105:A1202, an abstract from the
  chapter authors' group): compartment parameters did not relate
  straightforwardly to cardiac output or demographics, which the chapter reads
  as "correlating clearances and distribution volumes with tissue volumes and
  blood flows should be done with care, if at all" (p. 166).
- Rietbrock et al. 2000 (*Br J Anaesth* 84:437–42, PMID 10823092), paraphrased
  as Wissing's argument that "a precise allocation of several hypothetical
  peripheral compartments to anatomically defined tissues is hardly feasible"
  (p. 166).
- Hendrickx et al. 2006a (*BMC Anesthesiol* 6:7, PMID 16772041, a simulation):
  compartmental and physiologic models fit equally well, with a complex
  relation between their parameters (p. 166).

None disputes that the route exists; they dispute reading it off a washout fit.
Cite pp. 163 and 165–66 in the note's cautions, and record p. 165 beside
pp. 163 and 166 in `docs/references/README.md`'s Modern Anesthetics entry.

**Added 2026-09-27: the route has one source outside Eger's group, and it rests
on measurement rather than a washout fit.** Eger and Saidman rank their evidence
on p. 1025: a perirenal rim of anesthetic "directly demonstrates the movement of
anesthetic from kidney to fat (8)", nitrous oxide's diffusion through plastics
and membranes is "further evidence", and "the most convincing evidence" is the
elimination studies of refs 3–7, each of which names Eger among its authors in
PubMed. Refs 8 and 9, both checked in PubMed and neither in the private corpus:

- Ref 8: Allott PR, Steward A, Mapleson WW, *Br J Anaesth* 1976;48(4):279–95,
  PMID 1275995, doi:10.1093/bja/48.4.279, with no author in common with refs
  3–7. Per its abstract, seven dogs breathed 1% halothane for 80 min, and
  tensions measured in blood and a psoas biopsy were compared with a
  multi-compartment model quantified in each dog from measured organ masses,
  tissue solubilities, ventilation and cardiac output. They deviated "in a
  manner which could be attributed to metabolism of halothane and probably to
  direct diffusion of halothane from well-perfused organs and lean tissues into
  fat", and "[d]irect experimental evidence of diffusion into perirenal fat was
  obtained in supplementary experiments."
- Ref 9: Perl W, Rackow H, Salanitre E, Wolf GL, Epstein RM, *J Appl Physiol*
  1965;20(4):621–7, PMID 5838712, doi:10.1152/jappl.1965.20.4.621, which
  "suggested the importance of intertissue diffusion to anesthetic uptake and
  distribution 40 yr ago" (p. 1025). PubMed has no abstract for it.

So the route has independent support, in dogs and with halothane; its size does
not. The ~30% share and the 200–400 min time constants rest on refs 3–7, and
Carpenter et al. 1986's own abstract (ref 3, PMID 3706798) says only that the
fourth compartment's time constant "lies between the time constants predicted
for muscle and fat". Recommendation: the note's "Two cautions" make that split,
citing Allott et al. from its abstract with its species and agent, and cite
Perl et al. only as the paper that proposed the effect until its full text is
read. `docs/references/README.md` then owes an entry for whichever the note
cites.

Point 2's "Pp. 1024–25" and point 3's "P. 1024" were corrected on 2026-09-27
to p. 1025, where the corpus text dump's printed-page markers and pdftotext
both put the 30% passage and the lean-tissue passage.
