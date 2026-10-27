---
id: PL-2881
title: Specify the compartment schematic in docs/MODEL.md before it is drawn: what a fill height and an amount assert, how a vapour amount and a liquid-equivalent amount name their units, and the precision a compartment's amount is shown at
priority: P1
effort: M
status: ready
classes: safety, docs
feature: schematic
touches: docs/MODEL.md
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

**Checked 2026-10-27 (`PL-0S0V`): where the compartment amount's precision goes.** `AGENT_VOLUME_DISPLAY_DECIMALS` is now the run totals' entry in `app/formatting.py`'s `AGENT_AMOUNT_DISPLAY_PRECISION`, keyed by amount and unit. `AgentAmount.COMPARTMENT` has no entry in any unit, so `agent_amount_display_precision` refuses it until this item derives one. Add the entry for `AgentAmountUnit.MILLILITRES_OF_VAPOUR` with its `finest_decimals`, add its row to the table in `docs/MODEL.md` § "Displayed precision", and update `test_a_unit_with_no_derived_precision_is_refused`. `AgentAmountUnit` carries no spelling. The unit names this item sets belong in `DisplayUnit`, and the precision key should then read them, so the two do not name one unit twice.
