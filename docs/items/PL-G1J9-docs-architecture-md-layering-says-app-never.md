---
id: PL-G1J9
title: docs/ARCHITECTURE.md § 'Layering' says app/ never performs a unit calculation, but § 'Data flow' and the package map say chart_frame.py, formatting.py and agent_cost.py convert units; one statement is wrong (copy editor structure read, 2026-11-05)
status: untriaged
feature: architecture-md-structure
added: 2026-11-05
---

**Problem.** docs/ARCHITECTURE.md § 'Layering' says app/ never performs a unit calculation, but § 'Data flow' and the package map say chart_frame.py, formatting.py and agent_cost.py convert units; one statement is wrong (copy editor structure read, 2026-11-05)

**The structure read's query** (row numbers are docs/ARCHITECTURE.md at cfb15a4a, before the line edit):

- **Query, calculation in `app/`.** The file contradicts itself, and the statements stay as they are. Layering 29-32 says `app/` "never performs a physiological or unit calculation" and "only reads immutable snapshots". Against that:
  - Data flow 532-543 says `chart_frame.py` "converts each drawn value into the unit of its own axis".
  - Data flow 317-331 says `formatting.py` turns a fraction into a percent.
  - Package map 126 says `agent_cost.py` converts the delivered agent into millilitres of liquid.
  - Data flow 308-315 and Where new code belongs 1203-1236 say the views also read `drawn_window`.
