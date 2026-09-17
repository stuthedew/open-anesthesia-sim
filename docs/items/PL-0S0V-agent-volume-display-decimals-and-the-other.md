---
id: PL-0S0V
title: AGENT_VOLUME_DISPLAY_DECIMALS and the other display-precision constants are one Final per quantity, but once the unit is reader-selectable precision is a function of quantity AND unit, and docs/MODEL.md's derivation has to be per-unit too
priority: P2
effort: M
status: blocked
classes: safety, anticipated
blocked-by: PL-S6WW, PL-B396
feature: preferences-store
touches: src/anesthesia_sim/app/formatting.py, docs/MODEL.md, tests/unit
added: 2026-09-16
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

**Done when.** `docs/MODEL.md` § "Displayed precision" carries a derivation per
(quantity, unit) rather than per quantity; the constants express that shape
rather than one `Final` per quantity; the bound is one-sided with finer
precision refused rather than clamped; and a unit offered with no derivation
behind it fails loudly rather than formatting at a default. The two couplings
above are stated where a reader of `formatting.py` will meet them, so a later
session does not re-derive that a display constant is display-only.
