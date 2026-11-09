---
id: PL-KXRB
title: The interface's labels spell modelled, vapour, litres and millilitres the British way, while PL-XF89 settled the tree on US spelling and PL-SRXT moves docs/MODEL.md's own prose to it
priority: P3
effort: M
status: ready
classes: ux
touches: src/anesthesia_sim/app, tests/unit, tests/integration, docs/MODEL.md, README.md
added: 2026-11-09
payoff: A learner sees one spelling across the interface and the documents that quote it, so a label quoted in docs/MODEL.md still matches the screen once PL-SRXT moves that document to US spelling
verify: ! grep -qF '"Modelled concentrations' src/anesthesia_sim/app/dashboard_frame.py && ! grep -qF '"litres of vapour"' src/anesthesia_sim/app/formatting.py
---

**Problem.** The interface's labels spell modelled, vapour, litres and millilitres the British way, while PL-XF89 settled the tree on US spelling and PL-SRXT moves docs/MODEL.md's own prose to it

**What a learner sees.** The interface's text spells these words the British
way, and no interface string uses the US form. Counted on 2026-11-09 over the
string literals in `src/anesthesia_sim/app/` that are not docstrings: vapour
14, litres 8, millilitres 7, modelled 6 and millilitre 3, against none for
vapor, liters, milliliters or modeled. Examples are the readout heading
"Modelled concentrations: {agent}" (`COMPARTMENT_SUBSTANCE_TEMPLATE` in
`src/anesthesia_sim/app/dashboard_frame.py`), "Modelled, not measured" in the
same file, and the unit names "litres of vapour" and "millilitres of liquid" in
`src/anesthesia_sim/app/formatting.py` and `display_units.py`. The same screens
say "Vaporizer output" (`AGENT_COST_HEADING` in `agent_cost.py`), so one View
already mixes the two spellings. The code's own docstrings write "modeled".

**Why it matters.** `PL-XF89` settled the project's self-description against
the tree's US spelling (closed 2026-09-13), and `PL-SRXT` moves
`docs/MODEL.md`'s own prose to it. `PL-SRXT` keeps every quoted interface
label exactly as the screen shows it, so while the interface stays British the
specification must keep two spellings side by side. A learner who sees
"vapour" on screen and "vapor" in the document may wonder whether they name
two different things.

**Done when.** Every string in `src/anesthesia_sim/app/` that a learner can
read uses US spelling: modeled, vapor, liter and milliliter. The tests that
assert those strings, and every quotation of them in `docs/MODEL.md` and
`README.md`, change in the same branch, so a quoted label still matches the
screen. Docstrings and comments are outside this item. The wording and the
units shown do not change, only the spelling.

**Generator check.** One-off. The fact is which spelling the project's text
uses. `PL-XF89` decided it for `README.md` and `pyproject.toml`, and `PL-SRXT`
applies it to `docs/MODEL.md`. That is two items on one fact, and no head's
`misread:` states it. Not a re-entry of `PL-XF89`, whose scope was the
project's one-line self-description and which closed more than 30 days ago.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Present:
at `817a4d88`, `dashboard_frame.py` already held "Modelled" seven times and
`formatting.py` held "vapour" or "litres" fourteen times. The item is classed
`ux` only, which is not debt, so v0.7.0's gate does not take it.

**Found by** the 2026-11-09 triage pass, while checking `PL-SRXT`.

