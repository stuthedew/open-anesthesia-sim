---
id: PL-0S0V
title: AGENT_VOLUME_DISPLAY_DECIMALS and the other display-precision constants are one Final per quantity, but once the unit is reader-selectable precision is a function of quantity AND unit, and docs/MODEL.md's derivation has to be per-unit too
priority: P1
effort: M
status: done
classes: safety, anticipated
feature: preferences-store
touches: src/anesthesia_sim/app/formatting.py, docs/MODEL.md, tests/unit, ROADMAP.md, docs/items/PL-2881-specify-the-compartment-schematic-in-docs-model.md, docs/items/PL-B396-agent-amounts-are-displayed-in-litres-of-vapour.md, docs/items/PL-1P15-show-what-the-delivered-agent-cost-in-money-at.md, docs/items/PL-GL5X-load-factory-preferences-needs-shipped-defaults.md
blocked-by: PL-KZ99
deferred-from: v0.6.0 - deferred to Gate 3 on beat 3's terms (PL-DB64, project owner, 2026-09-27, ratified, over keeping it on the list): work planned-milestone item 28 would create, waiting on PL-B396; safety, but not live at 19af95d - agent amounts show in one fixed unit with no selector, so displayed precision is one quantity's
added: 2026-09-16
closed: 2026-10-27
pr: 1878
payoff: every agent amount on screen is shown at a precision derived for its quantity and its unit, so a liquid-equivalent millilitre figure claims no more precision than the model supports
verify: grep -q 'def test_a_precision_finer_than_its_derived_band_is_refused' tests/unit/test_formatting.py && grep -q 'def test_a_unit_with_no_derived_precision_is_refused' tests/unit/test_formatting.py
---

**Problem.** AGENT_VOLUME_DISPLAY_DECIMALS and the other display-precision constants are one Final per quantity, but once the unit is reader-selectable precision is a function of quantity AND unit, and docs/MODEL.md's derivation has to be per-unit too

**Why it is cheap now and expensive later.** `app/formatting.py` holds
`AGENT_VOLUME_DISPLAY_DECIMALS: Final = 1` — one decimal, in litres of
equivalent pure agent gas — with `AGENT_VOLUME_DISPLAY_RESOLUTION_L` derived
from it, and `docs/MODEL.md` § "Displayed precision" carries the derivation
(`PL-TG60`): one published SD of a partition coefficient moves the exhaust
total by 0.016-0.042 L at 1 h and 0.18-0.23 L at 24 h, so 0.1 L sits inside
the admitted band. That derivation is *about the litre*. It does not transfer.

**The same band in the units now decided.** At the sevoflurane 20 C ratio
(5.47 mL liquid per L of vapour) the band is 0.09-0.23 mL at 1 h and
1.0-1.3 mL at 24 h, so 0.1 mL and 1 mL fall on opposite sides of it and
neither inherits the existing argument. In money it depends on a price the
reader sets, so the resolution is not even a constant.

**So the shape has to change, not just the number.** A single module-level
`Final` per quantity assumes one unit per quantity forever. Once the reader
picks the unit, precision is a function of (quantity, unit) and
`docs/MODEL.md` owes a derivation per unit. Deciding that shape before the
liquid-millilitre readout is built costs nothing; retrofitting it means
touching every readout and re-opening every derivation in that section.

**Why it matters.** Precision is not one thing here, and the tempting summary —
"precision follows the unit, so it is derived rather than stored" — is true of
only part of the file. `docs/MODEL.md` § "Displayed precision" derives a *band*
whose ceiling is model fidelity and records that the count inside it is a
presentation decision the owner may revise without re-deriving anything in
`core/` (`PL-88GQ`). So the three constants have three different derivations:
`MAC_DISPLAY_DECIMALS` is derived and test-enforced, `CONCENTRATION_DISPLAY_DECIMALS`
is the owner's pick inside a band, and `WASH_IN_DISPLAY_DECIMALS` is set by
Yasuda's published SDs. None of them is derived from "the unit".

**And display precision is not display-only, which is the safety half.**
Measured 2026-09-17, both first-hand:

- `WASH_IN_DENOMINATOR_FLOOR_FRACTION` is derived from
  `CONCENTRATION_DISPLAY_RESOLUTION_PERCENT` (`src/anesthesia_sim/app/wash_in.py`,
  "Derived rather than chosen"). It is the smallest inspired fraction the
  F_A/F_I ratio may be formed from — a **scientific domain boundary**, moved by a
  factor of ten per decimal.
- `CONCENTRATION_DISPLAY_DECIMALS` and `FLOW_DISPLAY_DECIMALS` are passed into
  the parameter controls in `src/anesthesia_sim/app/dashboard_frame.py`, so they
  set the slider step and therefore **the set of reachable model inputs**.

A reader-settable precision would move both. That makes this `safety`-classed
rather than a formatting convenience, and it means the bound has to be
**one-sided**: coarser is always safe, finer is refused rather than clamped, on
the `PL-0MLQ` precedent that a range outside the verification domain is refused.

**Blocked on two things, both real.** `PL-S6WW` fixes the reference temperature,
and the mL band moves 5.8% between a 20 C and a 37 C reference — which moves the
numbers this item's whole argument rests on. `PL-B396` is the millilitre readout
whose precision is in question and is itself undecided between two options.
Nothing here is actionable until both land; `AGENT_VOLUME_DISPLAY_DECIMALS` is
correct for the unit currently displayed.

[superseded 2026-10-25: v0.7.0 schedules item 28, and this item now waits on `PL-KZ99`]
**Where the two stand, 2026-09-27 (`PL-18BD`).** `PL-S6WW` closed on
2026-09-17. `PL-B396` is no longer undecided: its unit was settled on
2026-09-16 as millilitres of liquid equivalent by default, and it is now
`blocked` on `PL-YRLM`, which holds whether a release schedules the readout
(planned-milestone item 28). So this item waits on that release, reached
through `PL-B396`, and `ROADMAP.md` defers it to Gate 3 with `PL-B396`
(`PL-DB64`).

**Done when.** `docs/MODEL.md` § "Displayed precision" carries a derivation per
(quantity, unit) rather than per quantity; the constants express that shape
rather than one `Final` per quantity; the bound is one-sided with finer
precision refused rather than clamped; and a unit offered with no derivation
behind it fails loudly rather than formatting at a default. The two couplings
above are stated where a reader of `formatting.py` will meet them, so a later
session does not re-derive that a display constant is display-only.

**Scheduled in v0.7.0, 2026-10-25.** `PL-LF0P` scoped v0.7.0 with planned-milestone item 28, agent cost, inside it (project owner, 2026-10-25, ratified, over leaving item 28 unscheduled and deferring this item to Gate 4). `PL-YRLM` closed with that answer. This item is in `ROADMAP.md` § "v0.7.0 - the schematic" → "Required scope", so v0.7.0 clears it itself.

[superseded 2026-10-26: `PL-KZ99` closed, and the ratio is `AgentParameters.vapour_volume_per_liquid_volume`]
**It waits on `PL-KZ99` instead of `PL-B396`.** The per-unit precision of a
liquid-equivalent figure depends on the vapour-to-liquid factor `PL-KZ99`
stores. `PL-B396`'s readout then uses this item's derivation.

**Checked 2026-10-25 (`PL-F2NX`, Gate 3's staleness sweep): still true, but this brief asks for more than v0.7.0 needs.** The constants are as described, and `docs/MODEL.md` § "Displayed precision" still derives one precision per quantity. Entry 7 of v0.7.0's Required scope asks for a precision per quantity and per unit, for the units v0.7.0 offers: litres of vapour and millilitres of liquid equivalent on the agent cost View, and the schematic's millilitres of vapour, whose precision `PL-2881` derives. Nothing scoped lets a reader set a precision, and no concentration or flow gets a unit selector. So in v0.7.0 the one-sided bound in **Done when** has no reader setting to refuse. This sweep reads it, for now, as a test that refuses a precision constant finer than its derived band. Separately, the comment above `FLOW_DISPLAY_DECIMALS` in `app/formatting.py` is out of date: it still names Flet's default and says a flow reaches `core/` unquantized, but `ParameterControl.decimals` sets the slider's step. Correcting it is part of this item, which states that coupling where a reader of `formatting.py` meets it.

**Ready, 2026-10-26.** `PL-KZ99` closed on #1866, so the input this item
waited on exists. `AgentParameters.vapour_volume_per_liquid_volume` gives the
millilitres of vapour per millilitre of liquid: 182.8 for sevoflurane, 195.8
for isoflurane and 209.7 for desflurane. `core/liquid_agent.py`'s
`liquid_volume_ml` converts an amount with it. Nothing else holds this item.
`PL-B396` uses this item's derivation, so this item comes first.

**Re-confirmed 2026-10-27: still true, worked to the 2026-10-25 sweep's reading.** The constants were as the brief says, and `docs/MODEL.md` derived one precision per quantity.

**What was built, 2026-10-27.**

- `app/formatting.py` replaces `AGENT_VOLUME_DISPLAY_DECIMALS` and `AGENT_VOLUME_DISPLAY_RESOLUTION_L` with `AGENT_AMOUNT_DISPLAY_PRECISION`, keyed by `AgentAmount` and `AgentAmountUnit`. Each entry is an `AgentAmountPrecision`, which reads the finest derived count for its amount and unit and refuses a finer count, or a pair with no derivation, when it is built. `format_agent_volume` reads the run totals' shared litre count.
- The three totals each keep one decimal in litres of vapour (`PL-TG60`). The delivered and exhausted totals are shown in whole millilitres of liquid: one count of 0.1 L of vapour is 0.48-0.55 mL of liquid across the three agents, and 1 mL is the finest power of ten at or above that. The parameter spread agrees: the 24 h exhaust shift is 0.92-1.10 mL of liquid. The stored total is refused in liquid, because the conversion reads a store 5.8% high, which is more than one count above about 17 mL. A compartment's amount has no entry until `PL-2881` derives one, and money is `PL-1P15`'s.
- `docs/MODEL.md` § "Displayed precision" has the per-amount, per-unit table, the liquid derivation, what is not yet derived, and the two couplings: the concentration and flow counts set the slider steps, and the concentration resolution sets the F_A/F_I denominator floor. `formatting.py` states both couplings at the constants, and the stale Flet wording in the `FLOW_DISPLAY_DECIMALS` comment is corrected.
- Concentration, flow, MAC and F_A/F_I keep one count each. Each is shown in one unit in v0.7.0, so a per-unit table for them would have one entry each. `docs/MODEL.md` says a unit selector for any of them moves its count into a table of the same shape.
- Tests in `tests/unit/test_formatting.py`: `test_a_precision_finer_than_its_derived_band_is_refused`, `test_a_unit_with_no_derived_precision_is_refused`, and `test_a_run_total_in_millilitres_of_liquid_claims_no_more_than_in_litres_of_vapour`, which re-derives the liquid count from each agent's stored molar mass and density. The new tests need the new interface, so they cannot be collected on the code before this change. Nothing displayed changed, so there is no regression to replay.
- Briefs of `PL-2881`, `PL-B396` and `PL-1P15` carry a dated note saying where their entry goes, and `ROADMAP.md`'s scope entry 1 and `PL-GL5X` name the new table.


**Held for the owner's read, 2026-10-27.** The derivation is a new statement in `docs/MODEL.md` of how precisely a displayed clinical amount may be shown, so pull request #1878 waits on the owner. The thing to check is the table and the two paragraphs under it in § "Displayed precision": whole millilitres for the delivered and exhausted totals in liquid, and the stored total refused in liquid.
