---
id: PL-YVHK
title: Implement the chart hover readout on pyqtgraph to the derivation docs/MODEL.md now carries, turn hoverable on so the affordance is not silently lost, and say in README.md that it exists
priority: P1
effort: S
status: blocked
blocked-by: v0.5.1
classes: safety, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/chart_series.py, src/anesthesia_sim/app/simulation_view.py, README.md, tests/integration
added: 2026-09-14
verify: uv run pytest tests/unit/test_formatting.py && grep -rqF 'def test_the_hover_readout_states_the_agent_compartment_and_both_units' tests/
---

**Problem.** Implement the chart hover readout on pyqtgraph to the derivation docs/MODEL.md now carries, turn hoverable on so the affordance is not silently lost, and say in README.md that it exists

**This is `PL-YLKR`'s other half.** That item asked what a chart tooltip should
say and was split on the project owner's decision of 2026-09-14: the design and
its derivation landed then, in `docs/MODEL.md` § "The chart's hover readout:
what the tooltip may show", and the implementation waits for the toolkit it
will be written against. Nothing here is open design work. Read that section
first; it is the specification, and this item is the build.

**What it owes, in one list.**

1. **The three-line content**, exactly as the derivation states it: run context
   (the modelled marker, the agent, the instant), then the compartment with its
   gloss where the readout row has one, then the value in both units.
2. **Every number through `app/formatting.py`** — `format_percent`,
   `format_mac_multiple`, `format_elapsed`, and `format_wash_in_ratio` for the
   wash-in trace. Never through the chart library's own formatter, which is
   what the derivation's measured table is about.
3. **The MAC multiple against the snapshot's own `mac_percent`**, exactly as
   the MAC axis and the readout row resolve it.
4. **`hoverable` turned on**, for the six compartment traces and the wash-in
   trace and for nothing else. The clinical references and the control marks
   stay silent, for the interaction reason the derivation gives.
5. **`README.md` saying the affordance exists**, which it cannot say until it
   does.

**The one thing that will go wrong if nobody names it.**
`pyqtgraph.ScatterPlotItem` ships `'hoverable': False`, and a plotted line
carries no hover at all, so a port that says nothing about this does not
inherit the Flet build's hover — it loses it. `v0.5.1`'s own definition of done
is "every capability the Flet build has, the Qt build has", so silence here is
a parity failure rather than a deferral. `PL-DNHM` recorded the finding and is
closed onto this item.

**Why it is `blocked-by: v0.5.1` rather than done on Flet.** Implementing on
`flet_charts` means writing a `text` string onto every one of roughly 1 870
point objects, onto a pause-transition frame `PL-KP7H` already measured at
71.9 ms and 90 KiB — and then deleting all of it, because under pyqtgraph the
same content is one format callable evaluated when the pointer arrives. The
shipped Flet build therefore keeps `PL-KP7H`'s paused-only hover and its
library-default contents until the port. That is a stated cost of the split
rather than an oversight: the interim build shows a bare number on hover, and
the derivation says why that is wrong.

**Done when** a hover over each of the six compartment traces and over the
wash-in trace reports what § "The chart's hover readout: what the tooltip may
show" specifies, at the readouts' own resolution and with the below-resolution
forms intact; the references and control marks report nothing; `README.md`
names the affordance; and a headless test holds the rendered string against a
real controller rather than against a formatter in isolation.

**Why it matters.** A number somebody stopped the simulation to read is one
they will act on, and this is the one display in the interface where a value
appears with nothing around it — no heading naming the agent, no legend naming
the compartment, no row of five other compartments making a within-run
comparison obviously what is on offer. Every qualifier the readout row gets
from its surroundings, the hover has to supply itself, and what a chart library
supplies instead is a coordinate: `.3g` on the drawn y prints `3.52e-05` on the
fat compartment at 48 s, where the readout beside it says `<0.01%` — five
decimal places past the resolution this project derives, with no unit, on a
chart carrying two axes that differ by a factor of two.

The second half is quieter and is why this is `P1` rather than a polish item.
The affordance does not survive the port by default. `hoverable` is `False` and
a line has no hover, so unless this is built the Qt chart answers nothing, no
test notices, and the interface loses a capability the parity criterion says it
keeps.
