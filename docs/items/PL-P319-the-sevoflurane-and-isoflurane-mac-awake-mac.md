---
id: PL-P319
title: The sevoflurane and isoflurane mac_awake.mac_reference_basis cannot name the base MAC in percent or the age correction Katoh 1993 used, because the abstract gives neither and the full paper is not in the reference corpus; read the paper and name both, and state the form of Katoh's brain-uptake calculation in docs/MODEL.md
priority: P1
effort: S
status: done
classes: docs, science
feature: mac-awake-reference-text
milestone: v0.6.9
touches: src/anesthesia_sim/data/agents/sevoflurane.json, src/anesthesia_sim/data/agents/isoflurane.json, docs/MODEL.md, docs/references/README.md, docs/references/katoh-1993-anesth-analg-mac-awake-washout.md
added: 2026-10-26
closed: 2026-10-26
pr: 1865
reason: the project owner added the full text of Katoh 1993 (PMID 8214700) and its companion age paper (PMID 8424514) to the reference corpus on 2026-10-26, so the item is an ordinary edit
payoff: anyone can check which base MAC the sevoflurane and isoflurane MAC-awake fractions were measured against, and so how far each band sits from the source
verify: grep -qE '"mac_reference_basis": "[^"]*[0-9.]+ percent' src/anesthesia_sim/data/agents/sevoflurane.json && grep -qE '"mac_reference_basis": "[^"]*[0-9.]+ percent' src/anesthesia_sim/data/agents/isoflurane.json
---

**Problem.** Katoh T, Suguro Y, Kimura T, Ikeda K, Anesth Analg
1993;77(5):1012-1017 (PMID 8214700) reports MAC-awake "as a ratio to
age-adjusted MAC". The abstract does not say which base MAC or which age
correction the ratio uses, and the full paper is not in the reference
corpus. So since `PL-GCGX` (#1863) the `mac_awake.mac_reference_basis` in
`sevoflurane.json` and `isoflurane.json` says the base MAC is not recorded,
where desflurane's names 7.25 percent. The same gap leaves `docs/MODEL.md`
§ "MAC-awake as a chart reference" unable to say what form Katoh's
brain-uptake calculation takes (`PL-YDRT`).

**Why it matters.** A fraction with no stated denominator is the correct
number in the wrong context, as that section says. Without the base MAC,
nobody can check how far the stored fraction times the Gas Man `mac_percent`
sits from the absolute awakening concentration Katoh's patients reached.

**Done when.** The full paper has been read through the reference corpus.
Both `mac_reference_basis` strings name the base MAC in percent and the age
correction, and `docs/MODEL.md` states the form of the brain-uptake
calculation behind the "predicted" cerebral concentrations. This needs the
project owner to add the paper's PDF to `stuthedew/open-anesthesia-sim-references`.

**Found by.** `PL-GCGX` and `PL-YDRT` on #1863, 2026-10-26, from the PubMed
abstracts of PMID 8214700 and of the companion Katoh 1993 paper on age
(Anesth Analg 1993;76(2):348-52, PMID 8424514), neither of which gives the
base MAC.

**Decision (answered).** The project owner added both Katoh 1993 papers to
`stuthedew/open-anesthesia-sim-references` on 2026-10-26, in commit
`d7c743a`: the washout paper (PMID 8214700) and the companion age paper
(Anesth Analg 1993;76(2):348-52, PMID 8424514). That was the answer the
question above asked for, so the item became `ready` the same day.

**Done (2026-10-26).** The washout paper was read in full in the private
corpus. Its age-adjusted MAC is 2.56 − 0.0156 × age (yr) percent sevoflurane
and 1.43 − 0.0061 × age (yr) percent isoflurane (p. 1013), and both
`mac_reference_basis` strings now name these equations. The brain estimate is
one perfusion-limited compartment (equation 1, p. 1013). The abstract's
cerebral figures, 0.34 and 0.30 of MAC, use equation 3, which corrects the
end-tidal value for dead-space gas. With the arterial value taken as the
end-tidal value (equation 2) they are 0.30 and 0.26 (Table 1, p. 1014).
`docs/MODEL.md` and both agent files had quoted the abstract's figures
without saying which equation produced them, and now say so.
`docs/references/katoh-1993-anesth-analg-mac-awake-washout.md` holds the
values with their pages.
