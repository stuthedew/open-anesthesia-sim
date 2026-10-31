---
id: PL-YDRT
title: docs/MODEL.md and the Katoh 1993 source notes for sevoflurane and isoflurane say Katoh measured the brain concentration at awakening directly, but the paper's own title says the cerebral concentration was predicted, so a modelled estimate is recorded as a tier 1 direct measurement
priority: P1
effort: S
status: done
classes: docs, science
feature: mac-awake-reference-text
milestone: v0.6.9
touches: docs/MODEL.md, src/anesthesia_sim/data/agents/sevoflurane.json, src/anesthesia_sim/data/agents/isoflurane.json
added: 2026-10-25
closed: 2026-10-26
pr: 1863
payoff: the main evidence for reading the band against the vessel-rich trace is described as the model estimate it is, not as a measurement
verify: ! grep -qF 'directly rather than leaving it to inference' docs/MODEL.md && ! grep -qF 'directly rather than leaving it to inference' src/anesthesia_sim/data/agents/sevoflurane.json && ! grep -qF 'directly rather than leaving it to inference' src/anesthesia_sim/data/agents/isoflurane.json
---

**Problem.** `docs/MODEL.md` § "MAC-awake as a chart reference" says the paper "measures the brain concentration directly rather than leaving it to inference". The Katoh notes in `sevoflurane.json` and `isoflurane.json` say the same. The citation stored beside them is titled "Cerebral awakening concentration of sevoflurane and isoflurane *predicted* during slow and fast alveolar washout". Cerebral concentration cannot be sampled in surgical patients. The 0.34 and 0.30 ×MAC values at eye opening come from Katoh's own model of brain uptake.

**Why it matters.** This claim is the main evidence for reading the band against the vessel-rich trace. Calling a model output a direct measurement overstates that evidence, and it is the modelled-versus-measured confusion that `CLAUDE.md` forbids, applied to provenance. The rule may still be right, but the text should say what Katoh actually did, read from the paper through the reference corpus.

**Done when.** `docs/MODEL.md` and the Katoh 1993 notes in `sevoflurane.json` and `isoflurane.json` say the cerebral concentration at awakening was predicted by Katoh's model of brain uptake, read from the paper through the reference corpus, and none of the three says it was measured directly.

**Found by.** `PL-TBQS` reviewer replay on #288, findings r04 F2 and r05 F4. Checked against main on 2026-10-25: all three texts are unchanged.

**Closed on #1863 from the abstract, not the reference corpus** (2026-10-26).
The full Katoh 1993 paper is not in the reference corpus. Its PubMed abstract
(PMID 8214700, read 2026-10-26) says the brain concentrations were
"calculated with end-tidal anesthetic concentrations", and the title calls
them "predicted". `docs/MODEL.md` and both notes now say that, and say that
the form of the calculation is not recorded. `PL-P319` carries reading the
paper and stating that form.
