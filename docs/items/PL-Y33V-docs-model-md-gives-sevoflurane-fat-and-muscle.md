---
id: PL-Y33V
title: docs/MODEL.md gives sevoflurane fat and muscle time constants as about 42 h and 135 min in three chapters, but § 'Alveolar gas' tabulates 46 h and 172 min, and only § 'The first 24 hours...' says these are two kinds of time constant; each figure should say which kind it is (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: ready
classes: defect, docs
feature: model-md-structure
touches: docs/MODEL.md
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-11-05
payoff: a reader meeting 42 h in one chapter and 46 h in another learns that both are right and which kind each is, and can check the run-length argument against the table
verify: ! grep -qF 'fat group has a time constant of about 42 h' docs/MODEL.md && ! grep -qF 'muscle group has a time constant of about 135 min' docs/MODEL.md && ! grep -qF "muscle's time constant for sevoflurane is about 135 min" docs/MODEL.md
---

**Problem.** docs/MODEL.md gives sevoflurane fat and muscle time constants as about 42 h and 135 min in three chapters, but § 'Alveolar gas' tabulates 46 h and 172 min, and only § 'The first 24 hours...' says these are two kinds of time constant; each figure should say which kind it is (copy editor structure read, 2026-11-05)

**Checked 2026-11-09:** On cfd4a4b6, three places give sevoflurane's muscle and fat time constants as about 135 min and 42 h, without saying which kind. They are § "Supported run length" ("Why 24 hours ..."), § "Interface boundary" (the playback-rate paragraph) and § "The chart's time base". The table in § "Alveolar gas" gives the whole system's slowest terms at the default flows as 10 300 s and 167 000 s, which are 172 min and 46.4 h. Both sets are correct. The first set is each tissue's own time constant, volume times tissue:blood coefficient over blood flow (§ "Tissue uptake and return"). From the reference adult's data that is 33 L x (2.4/0.65) / (0.18 x 5 L/min) = 135 min for muscle, and 14.5 L x (34/0.65) / (0.06 x 5 L/min) = 2 528 min = 42.1 h for fat. The second set is the coupled system's time constants, which are longer because tissue uptake also has to fill the blood and gas phases. No displayed value is computed from either figure. They are used only to argue the run-length limit and the chart widths.

**Why it matters.** A clinician who compares the two sets sees two figures for one tissue, 42 h and 46 h, and cannot tell which the simulator runs on, or whether one is an error. A developer who checks the 24-hour run-length argument ("about 0.6 of the time constant") against the table gets 0.52 instead. The conclusion survives, but the reader cannot confirm it.

**Done when.** Each of the three places that give 135 min and 42 h calls them the tissue's own time constant and points to the equation in § "Tissue uptake and return". § "Alveolar gas" or one of those places says in one sentence that the coupled system's slowest terms, 172 min and 46 h at the default flows, are longer for the reason above.

**Generator check.** One-off: a finding from the `docs/MODEL.md` structure-read sweep. Two kinds of time constant are given under one name. No head's `misread:` states that fact.
