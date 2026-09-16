---
id: PL-0S0V
title: AGENT_VOLUME_DISPLAY_DECIMALS and the other display-precision constants are one Final per quantity, but once the unit is reader-selectable precision is a function of quantity AND unit, and docs/MODEL.md's derivation has to be per-unit too
status: untriaged
feature: preferences-store
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
