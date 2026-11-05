---
id: PL-GSPR
title: docs/ARCHITECTURE.md's package map says blood.py, tissue.py and circuit.py advance their own amounts, but § 'Data flow' says one exact propagation advances the whole coupled system; the map may be stale (copy editor structure read, 2026-11-05)
status: untriaged
feature: architecture-md-structure
added: 2026-11-05
---

**Problem.** docs/ARCHITECTURE.md's package map says blood.py, tissue.py and circuit.py advance their own amounts, but § 'Data flow' says one exact propagation advances the whole coupled system; the map may be stale (copy editor structure read, 2026-11-05)

**The structure read's query** (row numbers are docs/ARCHITECTURE.md at cfb15a4a, before the line edit):

- **Query, how a step is advanced.** The file contradicts itself. Package map 93 says `blood.py` and `tissue.py` "advance their amount" by the first-order approach, and `circuit.py` "advances its fraction". Data flow 185-206 says `advance()` moves the whole coupled system in one exact propagation, "not by a sequence of sub-exchanges", with one matrix-vector product for the six fractions. Is `exponential_approach.py` still used when a step is advanced, and if so, where?
