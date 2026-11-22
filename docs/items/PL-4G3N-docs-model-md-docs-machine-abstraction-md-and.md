---
id: PL-4G3N
title: docs/MODEL.md, docs/machine-abstraction.md and the model description draft repeat claims about Fukuda et al. 2006 and Shin et al. 2017 that the sources do not support
priority: P2
effort: S
status: done
classes: defect, docs
feature: anesthesia-machine
milestone: v0.6.19
touches: docs/MODEL.md, docs/machine-abstraction.md, docs/prose-review/model-description-draft.md, docs/machine-survey.md, docs/items/PL-CR81-projects-threads-in-the-v0-7-0-project-run.md
added: 2026-11-11
closed: 2026-11-22
pr: 2212
payoff: A clinician reading what the model leaves out is told only what Fukuda and Shin actually measured, not a stronger claim the sources do not make.
verify: grep -qF 'on the one machine where it was compared' docs/MODEL.md
---

**Problem.** docs/MODEL.md, docs/machine-abstraction.md and the model description draft cite Fukuda et al. 2006 for a rise in F_I/F_D at a fixed circuit volume and on every machine, which its abstract does not support. docs/machine-abstraction.md also gives a list of Shin et al.'s reasons that the paper does not support.

Found by `PL-KZ60` on 2026-11-11, while checking each claim of `docs/machine-survey.md` that the model specification uses against the depth its source was read at.

**What the source says.** Fukuda T, Fukunaga A, Toyooka H. *J Anesth* 2006;20(4):268-273, PMID 17072690, DOI 10.1007/s00540-006-0417-6. Only the abstract has been read, through the PubMed record, on 2026-09-19 and again on 2026-11-11. The full text was not reachable on 2026-11-11: PubMed Central does not hold it, the private reference corpus does not either, and Springer's article page answered with a redirect. The abstract reports three machines:

- On the ACOMA KMA-1300-III, the inlet next to the patient raised F_I/F_D significantly for isoflurane and for sevoflurane.
- On the Dräger Fabius GS, it raised F_I/F_D significantly for sevoflurane. The abstract reports no isoflurane comparison on this machine.
- On the Dräger NM-GS, "the NM-GS showed no significant changes in the FI/FD ratios".

The authors conclude for "two decoupling-style anesthetic machines (ACOMA and Fabius)". The abstract does not say whether moving the inlet changed the circuit's volume.

**What the three documents say instead.**

- `docs/MODEL.md` § "Where each stored value comes from", the paragraph that opens "**Volume is not the whole of the difference between machines**": "Fukuda et al. moved only the fresh gas inlet, with the machine and the volume held fixed. The inspired/delivered ratio of both isoflurane and sevoflurane rose significantly at low flow".
- `docs/machine-abstraction.md` § "Fresh gas inlet position is not modelled", the paragraph that opens "The survey's headline finding": "moving only the fresh gas inlet significantly raised the inspired/delivered ratio of isoflurane and of sevoflurane during low-flow anesthesia ... a machine changed it with volume held fixed". The same section also says "Every surveyed machine is such a machine, except the two that Fukuda et al. instrumented", which counts two machines where the abstract names three, one of them (the ACOMA) not in the survey's machine table.
- `docs/prose-review/model-description-draft.md` § "6.4 The breathing circuit": "Fukuda et al. (2006) moved only the fresh gas inlet, with the machine and its volume fixed, and the inspired-to-delivered ratio of isoflurane and sevoflurane rose significantly at low flow."

All three copy the survey's headline as it stood before `PL-KZ60`. `PL-4DCG` wrote the survey and the `docs/MODEL.md` sentence in one change on 2026-09-19 (#742), so no separate adopting step checked it.

**The Shin et al. claim, in `docs/machine-abstraction.md` only.** § "Question 5", fact 1, says: "Shin et al. attributed the remaining difference to inlet position, decoupling, ventilator drive and delivery mode." Shin HW et al., *BMC Anesthesiol* 2017;17(1):10, read at full text from PubMed Central (PMC5248460) on 2026-11-11, say that "only Primus has a decoupling system" and that "Perseus and Zeus have the blower-driven ventilators". So decoupling and ventilator drive do not differ between the Perseus and the Zeus. For those two machines the authors "posit that these differences were due to the equipment-factors other than known factors such as the circuit volume and FGF rate", and the factors they name that differ are the inlet's distance from the patient and the Zeus's mixing chamber in fresh-gas mode. `docs/machine-survey.md` § "The headline finding" now says this. The sentence after the quoted one, "Every one of those is in this model's `not_modelled` list", needs checking against the corrected list. A blind reviewer of #2112 found this copy.

**Suggested wording**, matching what `docs/machine-survey.md` now says: "Fukuda et al. moved the fresh gas inlet from beside the absorber to beside the patient. During low-flow anesthesia on two decoupling-style machines, F_I/F_D rose significantly for sevoflurane, and for isoflurane on the one machine where it was compared; a third machine showed no significant change. The abstract, which is all this project has read, does not say whether the move changed the circuit's volume." The point the `docs/MODEL.md` paragraph makes still holds on Shin et al.'s measurements: the Perseus A500 and Zeus IE have nearly the same circuit volume (3.3 and 3.2 L) and still differ significantly in time to target (full text read 2026-11-11, PMC5248460).

**Why it matters.** `docs/MODEL.md` is what a reader trusts about what the model leaves out. The overstated sentence tells a clinician that inlet position alone, at the same volume, changes the inspired fraction on every machine tested. The source supports less than that. No displayed value changes.

**Done when.** The Fukuda passages say what the abstract supports, the Shin passage says what the paper supports, or a full-text reading of Fukuda et al. supports the stronger sentence and its route is recorded. `docs/MODEL.md` is held for restructuring until `PL-48MX` closes, but a fact fix may land.

**Checked 2026-11-22**, at `d4e8200c`. All four passages are still there. `docs/MODEL.md` § "Where each stored value comes from" still says "Fukuda et al. moved only the fresh gas inlet, with the machine and the volume held fixed". `docs/machine-abstraction.md` still says "moving only the fresh gas inlet significantly raised the inspired/delivered ratio of isoflurane and of sevoflurane", still counts "the two that Fukuda et al. instrumented", and § "Question 5" still says "Shin et al. attributed the remaining difference to inlet position, decoupling, ventilator drive and delivery mode". The draft's § "6.4 The breathing circuit" still carries the Fukuda sentence. The `docs/MODEL.md` and `docs/machine-abstraction.md` Fukuda sentences were present at the freeze (`git show 0947408:docs/MODEL.md` and `git show 0947408:docs/machine-abstraction.md`). The Shin sentence was not.

**Generator check.** The misread fact is what a cited source supports, at the depth this project read it. Here a later document copied the survey's headline without reading the source again. No head's `misread:` line states that fact. `PL-4BGX` (closed 2026-11-20: `docs/MODEL.md` stated the vaporizers' altitude response more firmly than its sources) and `PL-XGLH` (open: values read from an abstract cited as if from the full text) misread the same fact, so it is a candidate generator. It is reported to the coordinator rather than recorded here, because no open item holds a fix to its cause.

**Done 2026-11-22.** Both sources were read again in this session through the PubMed server: Fukuda et al.'s record and abstract (PMID 17072690, DOI 10.1007/s00540-006-0417-6), and Shin et al.'s full text from PubMed Central (PMC5248460, DOI 10.1186/s12871-016-0294-y). The abstract and the paper say what this brief quotes.

- `docs/MODEL.md` § "Where each stored value comes from", the paragraph that opens "**Volume is not the whole of the difference between machines**", now gives Fukuda's result on two machines and the third machine's null result, says the abstract does not state whether the volume changed and so does not show on its own that volume was not the cause, and rests the point that volume does not explain the difference on Shin et al.'s Perseus A500 and Zeus IE in fresh gas mode (3.3 and 3.2 L from Dräger's stated volumes plus the 1.2 L patient circuit, and a significant difference in time to target).
- `docs/machine-abstraction.md` § "Fresh gas inlet position is not modelled" says the same for Fukuda. Its sentence that every surveyed machine has an unknown inlet position "except the two that Fukuda et al. instrumented" now says the survey records an inlet position for few machines: Shin et al. describe where the inlet joins the circle on three Dräger machines, and Fukuda et al. compared two positions on the Fabius GS without saying which one it ships with. § "Question 5", fact 1, now gives Shin et al.'s reasons as the paper states them, and says the model represents neither inlet position nor a mixing chamber, because its circuit is one well-mixed compartment. The planned `not_modelled` list, in the paragraph that opens "Refusal 4 is the one worth arguing for", names inlet position but not a vaporizer's mixing chamber, so the old sentence "Every one of those is in this model's `not_modelled` list" was removed rather than kept.
- `docs/prose-review/model-description-draft.md` § "6.4 The breathing circuit" says the same for Fukuda.
- The paragraph of `docs/machine-survey.md` that opens "**Every claim in this document**" said the two documents "still repeat" the claims. It now says this item corrected them, at the paragraph's end, so the next sentence's "the same day" still dates `PL-8ZD7` to 2026-11-11.

Files checked for another copy of either claim: `grep -rn "Fukuda\|Shin et al" docs README.md src` outside `docs/items/`. The remaining mentions in `docs/machine-survey.md` already state the corrected claims, and `docs/MODEL.md`'s other Shin et al. passages give only the apparatus volumes.
