---
id: PL-B396
title: Agent amounts are displayed in litres of vapour, which is not the unit a reader buys, fills or wastes agent in - report a liquid-equivalent millilitre figure
status: untriaged
feature: liquid-agent-consumption
added: 2026-09-16
---

**Problem.** Agent amounts are displayed in litres of vapour, which is not the unit a reader buys, fills or wastes agent in - report a liquid-equivalent millilitre figure

**Raised by the project owner, 2026-09-16.** Reading the accounting panel's
"Delivered: 0.4 L": a clinician fills a vaporizer from a 250 mL bottle of
liquid, so litres of vapour is a unit with no handle on it, while "you put 25
mL into the patient and sent 100 mL to the scavenger" lands against something
they have physically held. The observation is right and the goal is not in
question. What is open is where the figure goes.

**The unit today is correct, and the caption says so.** `delivered_agent_l` is
$\dot V_F F_D \Delta t$ — litres of *pure agent vapour* at the model's
reference conditions, which is the vaporizer's vapour output, not liquid.
`ACCOUNTING_UNIT_CAPTION` reads "Litres of equivalent pure agent gas" and
`docs/MODEL.md` § "Displayed precision" records that it is worded that way
"because a bare 'L' beside an anaesthetic agent invites the liquid reading"
(`PL-TG60`). So this is an addition, not a correction.

**Two options, and they are not close in cost.**

1. *Re-unit the existing panel.* Cheapest. But "Agent accounting validation"
   is a numerical-conservation diagnostic — its status word rules on the
   solver, not on the case — and its last two lines are a residual at 1e-14,
   which is meaningless in millilitres and meaningless to a clinician in any
   unit. Putting a figure a reader would act on clinically under a heading
   that names a developer instrument is the mode-confusion
   `.claude/rules/expert-review.md` lists under human factors.
2. *A consumption readout of its own,* with the validation panel left in gas
   litres. Delivered as mL of liquid equivalent — the bottle figure — a
   current burn rate in mL/h, and the exhausted/stored split labelled for what
   it is (`PL-H4N8`). This is the display that can carry the low-flow lesson,
   because the lesson is a comparison of delivered totals at equal alveolar
   concentration and needs the rate beside the flow that sets it.

**Either way: "liquid equivalent", never "liquid".** The agent in fat is not
liquid; the millilitre figure is a mass expressed as the liquid volume that
would produce it. Same rule as "modelled, not measured" elsewhere in the
interface.

**Displayed precision has to be re-derived, not carried over.**
`AGENT_VOLUME_DISPLAY_DECIMALS` is 0.1 L of vapour, derived in `PL-TG60` from
one published SD of a partition coefficient moving the exhaust total by
0.016-0.042 L at 1 h and 0.18-0.23 L at 24 h. In sevoflurane liquid
equivalent at a 20 °C reference (5.47 mL per L of vapour) that band is
0.09-0.23 mL at 1 h and 0.98-1.26 mL at 24 h, so 0.1 mL and 1 mL sit on
opposite sides of it and the choice is a fresh derivation. Note also that the
conversion factor is agent-specific, so one resolution has to hold for all
three.

**Blocked by `PL-S6WW` and `PL-KZ99`.** No displayed millilitre figure is
defined until the gas volumes' reference temperature is on record and the two
physical constants are stored with theirs.

**Out of the current milestone.** v0.4.26 is the Qt port, whose definition of
done is parity against a closed enumeration; a new readout is not parity. This
is interface work for after the port.
