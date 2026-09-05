---
id: PL-6580
title: Strip the concentration chart's explanatory prose down to legend and labels
status: untriaged
touches: src/anesthesia_sim/app/simulation_view.py
added: 2026-09-05
---

**Problem.** Everything above the plot is prose. Between the section title and
the chart the reader passes an axis-key line, two reference values, three
legend rows and four italic explanatory paragraphs — the MAC-multiple
convention, what unchecking a compartment does and does not do, what MAC-awake
asserts and which trace to read it against, and what a vertical control mark
is. Roughly a dozen lines of continuous text stand between the reader and the
chart, every run.

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
