---
id: PL-0VZ5
title: Correct the supported-ranges comment that says Kharasch's review measured how sevoflurane metabolism scales with dose from 0.35 to 9.5 MAC-hours
status: done
feature: model-claims-held-by-tests
touches: src/anesthesia_sim/core/supported_ranges.py
added: 2026-11-22
closed: 2026-11-22
pr: 2256
verify: ! grep -qF 'scales with dose only' src/anesthesia_sim/core/supported_ranges.py
---

**Problem.** The comment above the run-length limit in `src/anesthesia_sim/core/supported_ranges.py` says Kharasch's review "reports how sevoflurane's metabolism scales with dose only from 0.35 to 9.5 MAC-hours". The review's abstract (*Anesth Analg* 1995;81(6 Suppl):S27-38, PMID 7486145, read on PubMed on 2026-11-22) gives 0.35 to 9.5 MAC-hours as the range of exposure in the studies of peak fluoride timing. It says separately that peak fluoride is proportional to dose. `PL-5C1H` corrected the same sentence in `docs/INTERFACE.md`.

**Done when.** The comment says that the studies the review draws on gave sevoflurane over 0.35 to 9.5 MAC-hours, as `docs/INTERFACE.md` now does.

**Closed 2026-11-22.** The comment now says that in the studies the review draws on, sevoflurane was given over 0.35 to 9.5 MAC-hours only, as `docs/INTERFACE.md` does since `PL-5C1H`. Only a comment changed.

**Generator check.** The fact is whether a sentence about a cited source says what the source says. The `PL-5C1H` pass found the same overstatement in `docs/INTERFACE.md` and fixed both copies together, and no third copy exists (`grep -rn 'scales with dose only'` over `docs/` and `src/` found none on 2026-11-22). So this is one instance, not a generator.
