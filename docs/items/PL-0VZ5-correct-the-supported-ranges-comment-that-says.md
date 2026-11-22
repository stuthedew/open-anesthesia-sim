---
id: PL-0VZ5
title: Correct the supported-ranges comment that says Kharasch's review measured how sevoflurane metabolism scales with dose from 0.35 to 9.5 MAC-hours
status: untriaged
feature: model-claims-held-by-tests
touches: src/anesthesia_sim/core/supported_ranges.py
added: 2026-11-22
---

**Problem.** The comment above the run-length limit in `src/anesthesia_sim/core/supported_ranges.py` says Kharasch's review "reports how sevoflurane's metabolism scales with dose only from 0.35 to 9.5 MAC-hours". The review's abstract (*Anesth Analg* 1995;81(6 Suppl):S27-38, PMID 7486145, read on PubMed on 2026-11-22) gives 0.35 to 9.5 MAC-hours as the range of exposure in the studies of peak fluoride timing. It says separately that peak fluoride is proportional to dose. `PL-5C1H` corrected the same sentence in `docs/INTERFACE.md`.

**Done when.** The comment says that the studies the review draws on gave sevoflurane over 0.35 to 9.5 MAC-hours, as `docs/INTERFACE.md` now does.
