---
id: PL-SLFT
title: The HEIGHT_BAND docstring in core/rounding.py says a 0.01 percentage-point display step is 0.5% of 1 MAC of sevoflurane; at the stored 1.8% it is 0.56%, so the docstring still describes the 2.0% MAC sevoflurane had before MAC at age 40 (found by PL-JP7P's blind review)
status: untriaged
feature: model-claims-held-by-tests
added: 2026-11-23
filed-pr: 2268
---

**Problem.** The HEIGHT_BAND docstring in core/rounding.py says a 0.01 percentage-point display step is 0.5% of 1 MAC of sevoflurane; at the stored 1.8% it is 0.56%, so the docstring still describes the 2.0% MAC sevoflurane had before MAC at age 40 (found by PL-JP7P's blind review)
