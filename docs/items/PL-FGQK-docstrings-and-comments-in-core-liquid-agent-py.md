---
id: PL-FGQK
title: Docstrings and comments in core/liquid_agent.py, app/formatting.py and app/agent_cost.py restate the 5.8 % store bias and the 17 mL step computed from the 20 °C reference temperature, and no derived: marker can reach a docstring, so a change to REFERENCE_TEMPERATURE_CELSIUS leaves them stale with no refusal
priority: P3
effort: S
status: done
classes: defect, docs
feature: model-claims-held-by-tests
touches: src/anesthesia_sim/core/liquid_agent.py, src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/agent_cost.py
added: 2026-11-22
closed: 2026-11-22
pr: 2241
payoff: a developer who changes the reference temperature finds no stale percentage left in the code's comments
verify: ! grep -qF '5.8 %' src/anesthesia_sim/core/liquid_agent.py
---

**Problem.** Docstrings and comments in core/liquid_agent.py, app/formatting.py and app/agent_cost.py restate the 5.8 % store bias and the 17 mL step computed from the 20 °C reference temperature, and no derived: marker can reach a docstring, so a change to REFERENCE_TEMPERATURE_CELSIUS leaves them stale with no refusal

**Found by** `PL-SD5V` on 2026-11-22, which tied the document copies of these figures to the constant. `grep -rn "5\.8 \?%\|17 mL" src/anesthesia_sim --include=*.py` finds the copies: the module docstring and two function docstrings of `src/anesthesia_sim/core/liquid_agent.py`, a docstring and a comment in `src/anesthesia_sim/app/formatting.py` (the comment gives the 17 mL), and the module docstring of `src/anesthesia_sim/app/agent_cost.py`. A `derived:` marker is read only in the documents, so nothing refuses these when the reference temperature changes. A fix could point each at `docs/MODEL.md` § "Units and symbols" instead of restating the figure.

**Built 2026-11-22.** Each of the six copies now names the cause in words and points at the document that holds the figure: `docs/MODEL.md` § "Units and symbols" for the 5.8 % (its `derived:` markers tie it to `REFERENCE_TEMPERATURE_CELSIUS`), and `docs/INTERFACE.md` § "Agent amounts in millilitres, and the cost" for the 17 mL. `grep -rn "5\.8 \?%\|17 mL" src/anesthesia_sim --include=*.py` now finds nothing. The comment in `app/formatting.py` still gives figures that the liquid density's SD sets (0.3 SD, half a millilitre); those do not follow from the reference temperature and are outside this item.

**Generator check.** Stock of the fact `PL-SD5V` worked: the link between a sentence and the tree fact it restates (`PL-4FBP`), here in code comments, which no `derived:` marker reads. `PL-SD5V` left these copies to this item on purpose, so this is not a re-entry. The fix removes the copies instead of adding a marker, so no copy is left to go stale.
