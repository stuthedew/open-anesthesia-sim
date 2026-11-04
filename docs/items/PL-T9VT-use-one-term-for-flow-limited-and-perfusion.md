---
id: PL-T9VT
title: Use one term for flow-limited and perfusion limited in docs/MODEL.md, and define it
priority: P2
effort: S
status: done
classes: docs
feature: prose-quality
touches: docs/MODEL.md
added: 2026-11-04
closed: 2026-11-04
pr: 2027
payoff: a clinician reading the model specification meets one defined term for exchange that blood flow limits, and no sentence calling arterial blood itself limited
verify: ! grep -q -i -E 'flow-limited|perfusion limited' docs/MODEL.md && grep -q 'Perfusion-limited exchange' docs/MODEL.md
---

**Problem.** `docs/MODEL.md` uses two terms for one property and defines neither: "flow-limited" appears in 9 places and "perfusion limited" in 6, counted on 2026-11-04 after `PL-9331`'s rewrite. Both mean uptake that blood flow limits, as opposed to uptake that diffusion limits. Pick one term and define it once beside its contrast with diffusion-limited exchange. In the definition, say that the term describes a tissue's or the lung's exchange with blood, not the blood itself, because several places say "arterial blood is flow-limited". West and Luks (*West's Respiratory Physiology: The Essentials*, 10th ed., 2016, chapter 3, "Diffusion") set out perfusion and diffusion limitation in the lung, and Jones and Rowland-Yeo (*CPT Pharmacometrics Syst Pharmacol* 2013;2:e63, doi:10.1038/psp.2013.41) use "perfusion rate-limited" for tissue kinetics.

**Reproduced 2026-11-04.** `grep -n -i -E 'flow-limited|perfusion[- ]limited' docs/MODEL.md` returns 15 lines. "flow-limited" is on 9 of them (the pathway diagram in § "Status", two sentences in § "Model boundary", the $`F_a`$ row of § "Symbols", the venous-blood and arterial-blood paragraphs, the stored-amount paragraph, the missing arterial-volume row, and the arterial-readout paragraph). "perfusion-limited" is on 4 and the unhyphenated "perfusion limited" on 2. Six of the nine "flow-limited" uses apply the term to arterial blood. None of the 15 defines either term.

**Why it matters.** A clinician who meets two names for one assumption has to guess whether they are two assumptions. "Arterial blood is flow-limited" also reads as a claim about the blood, when the assumption is about the lung's exchange with it. "Flow limitation" has a second meaning in critical care, expiratory flow limitation, which "perfusion-limited" does not share.

**Done when.** `docs/MODEL.md` uses "perfusion-limited" for every case and defines it once, in § "Model boundary", beside its contrast with diffusion-limited exchange. The definition says that the term describes the exchange between blood and the lung or a tissue. No sentence applies it to arterial blood.

**Decision, 2026-11-04.** "Perfusion-limited" is the term kept. `src/anesthesia_sim/core/tissue.py` and `docs/ARCHITECTURE.md` already use it. Jones and Rowland-Yeo use "perfusion rate-limited" for tissue, and Yasuda et al. use "perfusion- and not diffusion-limited" for these agents in volunteers. It also does not collide with expiratory flow limitation.

**Sources read.** Jones HM, Rowland-Yeo K. Basic concepts in physiologically based pharmacokinetic modeling in drug discovery and development. *CPT Pharmacometrics Syst Pharmacol* 2013;2:e63, doi:10.1038/psp.2013.41. Read in full from PubMed Central (PMC3828005) on 2026-11-04. § "PBPK model structure and assumptions" says each tissue is "typically described as either perfusion rate limited or permeability rate limited", and that perfusion rate-limited kinetics "tends to occur for small lipophilic molecules where the blood flow to the tissue becomes the limiting process". Yasuda N, Lockhart SH, Eger EI II, et al. Comparison of kinetics of sevoflurane and isoflurane in humans. *Anesth Analg* 1991;72(3):316-24, PMID 1994760, doi:10.1213/00000539-199103000-00007. Read from the private reference corpus's text layer on 2026-11-04: p. 319 assumes "that the delivery of anesthetic to the tissues is perfusion- and not diffusion-limited". West and Luks's chapter was not reached, because the corpus does not hold the book and no route here serves it, so `docs/MODEL.md` does not cite it.

**Generator check.** The fact is the name and meaning of the model's exchange assumption. No head's `misread:` states it, and no other open item misreads it. Two rewrites each kept the word they found, and `.claude/rules/plain-writing.md` point 3 already requires a term to be defined where it first appears. This is a one-off.
