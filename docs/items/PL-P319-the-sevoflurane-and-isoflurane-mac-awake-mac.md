---
id: PL-P319
title: The sevoflurane and isoflurane mac_awake.mac_reference_basis cannot name the base MAC in percent or the age correction Katoh 1993 used, because the abstract gives neither and the full paper is not in the reference corpus; read the paper and name both, and state the form of Katoh's brain-uptake calculation in docs/MODEL.md
priority: P1
effort: S
status: needs-decision
classes: docs, science
feature: mac-awake-reference-text
touches: src/anesthesia_sim/data/agents/sevoflurane.json, src/anesthesia_sim/data/agents/isoflurane.json, docs/MODEL.md
added: 2026-10-26
reason: waits on the project owner adding the full text of Katoh 1993 (PMID 8214700, not in PubMed Central) to the reference corpus
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

**Decision needed.** Can the project owner add the full text of Katoh T,
Suguro Y, Kimura T, Ikeda K, Anesth Analg 1993;77(5):1012-1017 (PMID 8214700,
DOI 10.1213/00000539-199311000-00024, read from PubMed 2026-10-26) to
`stuthedew/open-anesthesia-sim-references`? PubMed Central has no copy, so no
session can fetch it. Recommendation: add it, because v0.7.0's gate waits on
this entry. Once the PDF is in the corpus, the item is `ready` and is an
ordinary S-sized edit.
