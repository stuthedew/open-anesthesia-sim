---
id: PL-FBY3
title: docs/MODEL.md's intertissue-diffusion note records Eger and Saidman 2005 as abstract-only, though the private corpus now holds its full text, which confirms the note and adds a bias it does not name: the lean tissues that lose agent to fat equilibrate more slowly than a perfusion-limited group, the brain excepted
status: untriaged
feature: model-spec-accuracy
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
   fifth compartments in all four cohorts. Pp. 1024–25: elimination studies
   "indicate that intertissue diffusion accounts for approximately 30% of the
   anesthetic taken up (3–7)". Refs 3–7 are Carpenter 1986–87 and Yasuda 1991,
   all Eger's group, so the note's "Two cautions" should say this restates the
   interpretation rather than confirming it independently.
3. **A bias the note does not name.** P. 1024: part of the intestine, liver,
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
