---
id: PL-2881
title: Specify the compartment schematic in docs/MODEL.md before it is drawn: what a fill height and an amount assert, how a vapour amount and a liquid-equivalent amount name their units, and the precision a compartment's amount is shown at
priority: P1
effort: M
status: ready
classes: safety, docs
feature: schematic
touches: docs/MODEL.md, src/anesthesia_sim/app/formatting.py, tests/unit/test_formatting.py, docs/items/PL-RNYV-build-the-compartment-schematic-view-the.md, docs/items/PL-S79P-draw-each-compartment-s-share-of-the-agent-the.md, docs/items/PL-B396-agent-amounts-are-displayed-in-litres-of-vapour.md, docs/items/PL-KFTM-carry-each-compartment-s-modelled-agent-amount.md
added: 2026-10-25
payoff: docs/MODEL.md states what the schematic's heights, amounts and share bar assert, how vapour and liquid-equivalent amounts name their units, and the precision a compartment's amount is shown at, before any of it is drawn
verify: grep -qE '^#+ .*[Cc]ompartment schematic' docs/MODEL.md
---

**Where this came from.** `PL-LF0P` scoped v0.7.0, the schematic, on 2026-10-25. The project owner chose containers that fill to tension, labelled with their amounts, plus a bar showing each compartment's share of the agent (project owner, 2026-10-25, ratified, over containers drawn to scale and over Gas Man's Picture as it is). `ROADMAP.md` § "v0.7.0 - the schematic" has the reasoning and the measurements behind it.

**Problem.** The schematic will draw values a clinician could read as facts
about where the agent is, and `docs/MODEL.md` does not yet say what those
values assert. The safety-critical standard in `CLAUDE.md` puts the
specification before the drawing.

**What the subsection says.** It goes under § "Minimum displayed outputs".

- A container's fill height is the compartment's modelled tension, on one
  scale shared by every container of the run. A height is not an amount.
- A container's amount is the compartment's modelled agent, in the unit
  § "Agent amount" defines, labelled as vapour on the value itself.
- How a vapour amount and a liquid-equivalent amount name their units, once
  for the whole interface. The schematic labels its amounts in millilitres of
  vapour, and the agent cost View (`PL-B396`) gives millilitres of liquid
  equivalent. About 183 mL of sevoflurane vapour come from 1 mL of liquid, so
  a bare "mL" on either is a unit a learner can misread by a factor of about
  180.
- The displayed precision of a compartment's amount, derived in
  § "Displayed precision" the way `PL-TG60` derived it for the three totals.
  It must not inherit `AGENT_VOLUME_DISPLAY_DECIMALS`: at 0.1 L, venous blood
  and the alveoli read 0.0 L for a whole hour at 1 MAC.
- What the share bar shows: each compartment's amount as a share of all the
  agent the run holds, circuit included, and why a share on a common baseline
  is used instead of an area (Cleveland WS, McGill R, *J Am Stat Assoc*
  1984;79(387):531-554, https://doi.org/10.1080/01621459.1984.10478080).
- Why no container is drawn for arterial blood. This model gives arterial
  blood no amount of its own, because $`F_a \equiv F_A`$ (§ "Blood
  compartments").
- Two rows in the hazard table of § "Reasonably foreseeable misuse, and the
  hazards the presentation carries": a height read as an amount, and a vapour
  amount read as liquid.

**Why it matters.** `PL-KFTM`, `PL-RNYV` and `PL-S79P` build against this
text. Without it, each would decide the unit names and the precision on its
own.

**Done when.** `docs/MODEL.md` carries the subsection with every point above,
`tools/doc_check.py` is green, and the three build items cite it.

**Checked 2026-10-25 (`PL-F2NX`, Gate 3's staleness sweep): still true, with one figure to correct when the subsection is written.** `docs/MODEL.md` has no schematic subsection yet, and each section this brief cites exists. "Read 0.0 L" is not what the readout prints: `format_agent_volume` shows an amount below its resolution as "<0.1 L". And it holds for sevoflurane and isoflurane only. From the stored 2.5 L alveolar gas volume, desflurane's alveoli at 1 MAC (6%) hold about 0.15 L, which prints as 0.1 or 0.2 L. The conclusion is unchanged: a compartment's amount must not inherit `AGENT_VOLUME_DISPLAY_DECIMALS`. Entry 1 of v0.7.0's Required scope in `ROADMAP.md` repeats the figure.

**Checked 2026-10-27 (`PL-0S0V`): where the compartment amount's precision goes.** `AGENT_VOLUME_DISPLAY_DECIMALS` is now the run totals' litre entries in `app/formatting.py`'s `AGENT_AMOUNT_DISPLAY_PRECISION`, keyed by amount and unit. `AgentAmount.COMPARTMENT` has no entry in any unit, so `agent_amount_display_precision` refuses it until this item derives one. Add its derived count for `AgentAmountUnit.MILLILITRES_OF_VAPOUR` to `_FINEST_DERIVED_DECIMALS`, add its row to the table in `docs/MODEL.md` § "Displayed precision", and update `test_a_unit_with_no_derived_precision_is_refused`. `AgentAmountUnit` carries no spelling. The unit names this item sets belong in `DisplayUnit`, and the precision key should then read them, so the two do not name one unit twice.

**Written 2026-11-01.** `docs/MODEL.md` gains § "The compartment schematic:
what its heights, amounts and share bar assert", two rows in the hazard
table, and two rows and their derivation in § "Displayed precision". Four
choices were taken in the writing. Each is either derived by a rule the
project already holds, or is a placeholder under the rule that look, wording
and placement are placeholders while the interface is built (project owner,
2026-10-18).

- **The fill scale is the chart's own axis**, read from
  `chart_axis_top_percent` (3 MAC for every agent). A second scale for the
  schematic would be a second copy of a fact the chart already holds, and it
  would let one tension stand at two heights in two Views.
- **A compartment's amount is shown to two significant figures.** The
  derivation of `PL-X9KD` and `PL-TG60` was repeated on the amounts: one
  published SD of each coefficient, three agents, read at 10 min, 60 min,
  180 min and 24 h. The shift spans more than four orders of magnitude, from
  0.011 mL to 216 mL, so no count of decimals lies in the band that rule
  admits. 1 mL falls to a two-hundredth of an SD, and 10 mL hides venous
  blood for most of an hour. Relative to the amount the shift is 2.2% to 10%,
  and two significant figures put one count between a sixth of an SD and 124
  SDs. That is the finest count the rule allows, so it is the derived answer
  rather than a choice. The floor of 0.01 mL is a placeholder for legibility.
- **A share is shown in whole percent**, by the same derivation. One count
  lies between 0.8 SD and more than a hundred.
- **The unit spellings, "mL vapour" and "mL liquid equiv.", are placeholder
  wording.** The rule that every spelling names vapour or liquid is the
  requirement.

The measurement script and its output are in the session's scratchpad, not
the tree. It perturbed one coefficient at a time in a copy of the agent's
parameters and ran `AgentUptakeSystem` at the shipped 0.1 s step. The SDs
were 5.3% for sevoflurane, 6.4% for isoflurane, and 3.9% for desflurane's
tissue coefficients with 5.7% for its blood:gas coefficient, as § "Displayed
precision" records.
