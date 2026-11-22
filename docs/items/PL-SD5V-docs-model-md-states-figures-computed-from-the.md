---
id: PL-SD5V
title: docs/MODEL.md states figures computed from the 20 °C reference temperature (the 5.8 % store bias, 5.5 % fewer moles, 24.055 L/mol, the 17 mL step) with no derived: marker naming REFERENCE_TEMPERATURE_CELSIUS, so changing the reference temperature leaves them stale with no refusal
priority: P1
effort: S
status: done
classes: defect, safety
feature: model-claims-held-by-tests
touches: docs/MODEL.md, docs/INTERFACE.md
deferred-from: v0.7.0 - not live: checked 2026-11-22 at d4e8200c: REFERENCE_TEMPERATURE_CELSIUS is 20.0, and test_the_reference_condition_gap_is_the_ratio_of_molar_volumes computes the 5.8 % and 5.5 % from it, so every figure agrees with the constant and no learner can see a wrong value now
added: 2026-11-11
closed: 2026-11-22
pr: 2237
payoff: A change to the reference temperature can no longer leave the documents giving a clinician the wrong size for the liquid-conversion bias.
verify: grep -qF 'derived: 17 mL from core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20' docs/INTERFACE.md
reenters: PL-5L84
---

**Problem.** docs/MODEL.md states figures computed from the 20 °C reference temperature (the 5.8 % store bias, 5.5 % fewer moles, 24.055 L/mol, the 17 mL step) with no derived: marker naming REFERENCE_TEMPERATURE_CELSIUS, so changing the reference temperature leaves them stale with no refusal

**Found by.** Blind review pass 1 on `PL-5L84` (#2142). The reviewer changed `REFERENCE_TEMPERATURE_CELSIUS` to 25 in a copy of the tree, and the documentation check then reported only the paragraphs that write "20 °C". The figures computed from it stayed silent: "reads 5.8% high" and the 17 mL step in § "Displayed precision" (the paragraph saying the stored total is refused in millilitres of liquid), "the 5.8 % error" in the paragraph after it, the table row giving the reason the stored total is refused in liquid, "5.8 % high" and "5.5 % fewer moles" in § "Known limitations", and the 24.055 L/mol molar volume in § "Agent amount".

**Why it matters.** The 5.8 % bias is the reason the stored total is refused in millilitres of liquid. If the reference temperature changed and these figures did not, a reader would be given the wrong size for that bias, and no check would say so.

**Checked 2026-11-22**, at `d4e8200c`. `grep -n "derived:" docs/MODEL.md | grep REFERENCE_TEMPERATURE` prints nothing, so no figure carries a marker naming the constant as an input. The paragraphs that write "20 °C" now carry `provenance:` markers from `#2142`, which tie the 20 and not the figures computed from it. Since `#2109` moved the interface sections, some of the figures are in `docs/INTERFACE.md`: "reads 5.8% high", the row "The conversion reads a store 5.8% high", the 17 mL step and "the 5.8 % error". In `docs/MODEL.md`, the paragraph in § "Known limitations" that opens "`core/liquid_agent.py` is where an amount leaves the unit" says "reads a store 5.8 % high" with no marker at all. `test_the_reference_condition_gap_is_the_ratio_of_molar_volumes` in `tests/reference/test_known_limitations_figures.py` computes the 5.8 % and the 5.5 % from the constants, so today the figures and the constant agree.

**Done when.** Each figure computed from the 20 °C reference temperature, in `docs/MODEL.md` and in `docs/INTERFACE.md`, carries a marker naming `core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20` as an input, so the documentation check refuses the figure when the reference temperature changes. Where a figure also depends on 37 °C, which no module stores, the marker says so or the item records why it cannot be tied.

**Generator check.** A re-entry of `PL-5L84`, closed 2026-11-11, which tied each written 20 °C to the stored constant and left the figures computed from it untied. The misread fact is the link between a document sentence and the tree fact it restates, which `PL-4FBP` states.

**Done 2026-11-22**, on `claude/project-thread-v9awbd` from `c0e9861e`. Each figure computed from the 20 °C reference temperature now carries a marker of the form `<!-- derived: <figure> from core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->` under its paragraph, 14 in all. The restructure had moved some of the figures, so `docs/PARAMETERS.md` carries markers as well as the two files this item named.

1. `docs/MODEL.md` § "Units and symbols": 24.055 L/mol, and 5.5%, 5.8% and 1.058.
2. `docs/INTERFACE.md`: the table row "The conversion reads a store 5.8% high", the paragraph with "5.8%" and the 17 mL step, and the paragraph with "the 5.8 % error".
3. `docs/PARAMETERS.md` § "Agent amount": 24.055 L/mol, the factor of 1.058, and the 5.5 % and the 5.47 mL of the first reason; the note for developers that names the 5.8 % and 5.5 %; and the paragraph that says `core/liquid_agent.py` "reads a store 5.8 % high".

Check: with `REFERENCE_TEMPERATURE_CELSIUS` set to 25 in `src/anesthesia_sim/core/liquid_agent.py`, `uv run python tools/doc_check.py check` exits 1 and names all 14 markers ("24.055 L/mol was computed from core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20, but the file now holds 25"). With the constant restored it reports 0 errors.

**Why the 37 °C half is not tied.** The 5.5 %, the 5.8 %, the 1.058 and the 17 mL also depend on 37 °C, the temperature at which the partition coefficients were measured. No module under `src/anesthesia_sim/` stores it: the only copy is `BODY_TEMPERATURE_CELSIUS = 37.0` in `tests/reference/test_known_limitations_figures.py`, and a marker can name only a file under `src/anesthesia_sim/`. That test already computes the 5.8 % and the 5.5 % from both temperatures, so a change to the 37 is caught there. The 25.450 L/mol molar volume depends only on 37 °C and is left unmarked for the same reason. The derivation table in `docs/PARAMETERS.md` § "Agent amount" compares fixed temperatures that its columns name, so its figures do not move with the reference temperature and are left unmarked.

Files checked: `docs/MODEL.md`, `docs/INTERFACE.md`, `docs/PARAMETERS.md`, `docs/VERIFICATION.md` and `README.md`, by `grep -n "5\.8 \?%\|5\.5 \?%\|24\.055\|1\.058\|17 mL"`. The docstrings of `src/anesthesia_sim/core/liquid_agent.py`, `src/anesthesia_sim/app/formatting.py` and `src/anesthesia_sim/app/agent_cost.py` also state the 5.8 %, and no marker can reach a docstring; they are left as they are.
