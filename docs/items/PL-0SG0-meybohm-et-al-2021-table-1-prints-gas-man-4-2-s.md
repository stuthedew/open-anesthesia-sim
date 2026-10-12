---
id: PL-0SG0
title: Meybohm et al. 2021 Table 1 prints Gas Man 4.2's 1 MAC as 2.1% sevoflurane and 1.1% isoflurane where the three agent files store De Wolf et al. 2012's 2.0% and 1.2% as the same program's set, and no agent note records that the two tier-3 descriptions of Gas Man disagree on the MAC while agreeing on every partition coefficient
priority: P1
effort: S
status: ready
classes: science
feature: provenance
touches: src/anesthesia_sim/data/agents/sevoflurane.json, src/anesthesia_sim/data/agents/isoflurane.json, src/anesthesia_sim/data/agents/desflurane.json, docs/MODEL.md
added: 2026-10-11
payoff: a reader of the agent files can see that the two published descriptions of Gas Man's parameter set disagree on the sevoflurane and isoflurane MAC the display divides by
verify: grep -qF 'Meybohm' src/anesthesia_sim/data/agents/sevoflurane.json && grep -qF 'Meybohm' src/anesthesia_sim/data/agents/isoflurane.json && grep -qF 'Meybohm' src/anesthesia_sim/data/agents/desflurane.json
---

**Problem.** Meybohm et al. 2021 Table 1 prints Gas Man 4.2's 1 MAC as 2.1% sevoflurane and 1.1% isoflurane where the three agent files store De Wolf et al. 2012's 2.0% and 1.2% as the same program's set, and no agent note records that the two tier-3 descriptions of Gas Man disagree on the MAC while agreeing on every partition coefficient

**Found 2026-10-11, working `PL-QPN8`,** which read PMC7943506's tables from
PMC's XML record. Table 1, "Standard pharmacokinetic settings as used in Gas
Man (version 4.2)", prints 1 MAC as 6.0 desflurane, 2.1 sevoflurane and 1.1
isoflurane. Its blood/gas row (0.42, 0.65, 1.30) and its brain, muscle and fat
tissue/gas rows (0.54/1.10/2.10, 0.97/2.40/4.50, 13.00/34.00/70.00) are the
stored coefficients exactly, and its footnote says the settings "are based on
the work of Yasuda et al.", which is what `PL-FN5F` established for the
tissue:gas values. The three agent files store `mac_percent` 6.0, 2.0 and 1.2
on De Wolf et al. 2012's authority ("MAC values that we used in our Gas Man
simulations are: desflurane 6%, sevoflurane 2%, isoflurane 1.2%", quoted in
each file's Nickalls and Mapleson note), and neither file nor `docs/MODEL.md`
records that a second tier-3 description of the same program's set gives the
sevoflurane and isoflurane MAC differently.

**Why it matters.** Two tier-3 citations of one parameter set disagreeing on a
display divisor is a provenance fact a reader of the agent files cannot see,
and it bears on which figure is "Gas Man's" when the stored MAC is compared
against the age-40 meta-analysis in each file's Mapleson 1996 note (sevoflurane
2.0 reads 11.1% above 1.8; Gas Man 4.2's 2.1 would read 16.7% above). The
stored values do not change here: De Wolf is the adopted authority and
`docs/MODEL.md` § "Source hierarchy" admits a change only on a recorded
decision.

**Done when.** Each agent file's De Wolf note, or its `mac_percent` note,
records the Meybohm Table 1 figure beside the stored one, dated, and
`docs/MODEL.md`'s sentence on the two tier-3 citations says they disagree on
the MAC.
