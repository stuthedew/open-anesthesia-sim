---
id: PL-FGQK
title: Docstrings and comments in core/liquid_agent.py, app/formatting.py and app/agent_cost.py restate the 5.8 % store bias and the 17 mL step computed from the 20 °C reference temperature, and no derived: marker can reach a docstring, so a change to REFERENCE_TEMPERATURE_CELSIUS leaves them stale with no refusal
status: untriaged
feature: model-claims-held-by-tests
added: 2026-11-22
---

**Problem.** Docstrings and comments in core/liquid_agent.py, app/formatting.py and app/agent_cost.py restate the 5.8 % store bias and the 17 mL step computed from the 20 °C reference temperature, and no derived: marker can reach a docstring, so a change to REFERENCE_TEMPERATURE_CELSIUS leaves them stale with no refusal

**Found by** `PL-SD5V` on 2026-11-22, which tied the document copies of these figures to the constant. `grep -rn "5\.8 \?%\|17 mL" src/anesthesia_sim --include=*.py` finds the copies: the module docstring and two function docstrings of `src/anesthesia_sim/core/liquid_agent.py`, a docstring and a comment in `src/anesthesia_sim/app/formatting.py` (the comment gives the 17 mL), and the module docstring of `src/anesthesia_sim/app/agent_cost.py`. A `derived:` marker is read only in the documents, so nothing refuses these when the reference temperature changes. A fix could point each at `docs/MODEL.md` § "Units and symbols" instead of restating the figure.
