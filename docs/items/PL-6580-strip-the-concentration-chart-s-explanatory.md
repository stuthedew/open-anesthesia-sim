---
id: PL-6580
title: Strip the concentration chart's explanatory prose down to legend and labels
priority: P1
effort: S
status: done
classes: ux
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py, docs/MODEL.md
added: 2026-09-05
closed: 2026-09-08
pr: 479
verify: uv run pytest tests/unit/test_simulation_view.py && ! grep -q 'Left axis:' src/anesthesia_sim/app/simulation_view.py
---

**Problem.** Everything above the plot is prose. Between the section title and
the chart the reader passes an axis-key line, two reference values, three
legend rows and four italic explanatory paragraphs — the MAC-multiple
convention, what unchecking a compartment does and does not do, what MAC-awake
asserts and which trace to read it against, and what a vertical control mark
is. Roughly a dozen lines of continuous text stand between the reader and the
chart, every run.

**Raised to P1 on 2026-09-08** (project owner). The owner made the same
finding a second time, three days after this item was filed, looking at the
same screen: "I thought we got rid of that as this is for anesthesia
professionals." A P2 that the queue never reaches is mis-priced when the
finding it records keeps being re-made, and this is the only item that removes
what is being looked at. `PL-B89V` (name the interface's reader in a
path-scoped rule) was opened the same day and stops the *next* panel arriving
the same way; it does not touch this screen, which is why raising this one is
not made redundant by it.

**Why it matters.** The audience is an anesthesia provider, not a lay reader
(project owner, 2026-09-05). MAC, MAC-awake, the endpoint difference between
them, and what a tissue compartment is are fundamental knowledge for that
audience. Explaining them on the chart is not caution, it is talking down to
the reader — and it costs the thing the chart is for. A panel that has to be
read before the plot can be seen is a worse teaching instrument than a clean
one, however correct each sentence in it is.

The safety-critical standard is satisfied by labels here, not by prose. What
it requires is that a displayed value be traceable to the model, units and
divisor that produced it, and that modelled quantities not read as measured
ones. The two reference lines do exactly that and stay. The paragraphs are
tutorial, and `docs/MODEL.md` is where the full statement of each already
lives.

**Scope.**

Delete, in `src/anesthesia_sim/app/simulation_view.py`:

- the four italic `ft.Text` paragraphs — MAC-multiple convention (~1486),
  unchecking a compartment (~1523), MAC-awake (~1570), control marks (~1600);
- the axis-key line (~1467-1469, "Left axis: … | Right axis: … | Horizontal
  axis: …"). Both axes already carry their own titles on the chart —
  `left_axis` title "percent" (~793) and `self._mac_axis` title "multiples of
  1 MAC" (~736) — and the horizontal window is named by the time-base
  dropdown beside the section title, so the line is duplication in all three
  parts.

Keep:

- the three legend rows (compartments, clinical references, run record), and
  their row labels, which are what distinguishes a modelled trace from a
  published constant from a user input;
- `self._mac_reference_text` and `self._mac_awake_reference_text` (~849, ~859)
  — "1 MAC sevoflurane = 2.0%" and the MAC-awake fraction, divisor and band.
  These are the traceability the safety standard asks for, in the form it asks
  for it: named values, not explanation.

**Open, and small.** Whether the two axis titles are the right words once they
are the only ones. "percent" is ambiguous between vol % and % of a scale;
"vol %" or "% atm" says which. "multiples of 1 MAC" could be "× MAC". Decide
with the panel stripped and the chart in front of you rather than in advance.

**Done when.**
- Above the plot: the section title, the time-base control, the two reference
  values, and the three legend rows. No sentences.
- Both axes are titled on the chart itself.
- `docs/MODEL.md` still carries the full statement of the MAC-multiple
  convention (§ "MAC multiples as a display unit") and of the MAC-awake band;
  removing the interface copy must not leave either undocumented.
- `make check` clean, and the interface-render check updated for the smaller
  panel (see PL-7J96, make the interface renderable in a check).

**Resolved.**

*The axis titles, which the brief left open to be decided with the panel
stripped.* Left: `percent` → `% of 1 atm`. Not `vol %`, which the brief
offered: a volumes percent is a gas-phase volume fraction, which the circuit
and alveolar compartments have and the mixed-venous, vessel-rich, muscle and
fat compartments do not — those hold a partial pressure that convention quotes
as a percentage of an atmosphere, which is the phrase `docs/MODEL.md` already
uses for all six. An axis titling every trace as a volume fraction would
assert of four of them a quantity they do not have. Right: `multiples of
1 MAC` → `×MAC`. The brief's own suggestion, and it is right for a reason
beyond brevity: `formatting.MAC_UNIT_SUFFIX` is that exact token, carried by
every numeric MAC readout on the page under a safety argument `docs/MODEL.md`
states — "0.80 MAC" is read as a depth of anesthesia, "0.80 ×MAC" as the ratio
it is. The axis ticks read bare numbers, so the title is the only thing saying
what they are, and it labels six traces at once, five of them not the
compartment MAC is defined for. One unit, one token.

*The axis-key line was not deleted whole.* Its first two thirds went, being
duplication of the axis titles. The horizontal third stayed, reduced from
`Horizontal axis: simulated time, whole run so far, 45 min shown` to
`whole run so far, 45 min shown`. The brief reasoned that the time-base
dropdown names the window, which holds for a chosen rung and not for "Fit
run" — the default, where the selector names the *rule* and the caption is the
only thing that says what the rule came out as. `PL-012` required that and
`docs/MODEL.md` § "The chart's time base" still does. It is a state label
rather than explanation, so it belongs with the reference values the brief
keeps.

*Two things the deleted prose carried are not tutorial, and moved into the
legend rather than going with it.* `docs/MODEL.md` § "Interface boundary"
exempts a reference from the drawn-trace rule — no sample places it — and
bounds that exemption with a labelling requirement: a reference must state its
value and divisor **and name the compartment it is read against**. Only the
paragraphs did the last part. So the band reads `MAC-awake (population, ±1 SD;
read against vessel-rich trace)` and the line `1 MAC, reference adult
(alveolar)`. This is the one place the work goes beyond the brief's deletion
list, and it is six words in two labels. It is not caution: the alveolar trace
crosses the band about 2.3x earlier than the vessel-rich one, and every way of
pairing a reference with the wrong trace here shortens the apparent time to
awakening. If the labels read as too long, the vessel-rich clause is the one
to argue about; dropping it needs § "Interface boundary" amended first.

*What was left alone.* The wash-in section below the plot keeps its three
paragraphs — out of scope here, and its docstring argues they correct
expectations a reader brings *to that graph* rather than teaching what they
know. Whether the same case can be made after this pass is a separate
question, filed as its own item.
