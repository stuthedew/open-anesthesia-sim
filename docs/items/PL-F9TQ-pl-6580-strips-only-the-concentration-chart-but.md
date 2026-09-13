---
id: PL-F9TQ
title: PL-6580 strips only the concentration chart, but the wash-in panel's two paragraphs are the largest standing prose block on the screen and no item covers them
priority: P2
effort: S
status: done
classes: ux
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py, tools/contrast_check.py
added: 2026-09-08
closed: 2026-09-13
verify: uv run pytest tests/unit/test_simulation_view.py -q -k "wash_in_heading_and_its_plot or wash_in_plot_says_what_its_denominator"
---

**Problem.** Measured 2026-09-08 over `app/simulation_view.py` with `ast`: 29
`ft.Text` string literals, 2,465 characters, of which 1,868 are the seven
italic explanatory paragraphs. `PL-6580` (strip the concentration chart's
explanatory prose) names four of the seven and one of the two axis-key lines,
all in the compartment-chart panel. Executed exactly as written it leaves:

- `_build_wash_in_section`'s two paragraphs, 346 and 440 characters — the F_I
  denominator, and the held-constant caveat. 786 characters, the largest
  standing block on the screen, and larger than any single block `PL-6580`
  removes;
- the run-record note under the control timeline, 87 characters;
- the wash-in axis-key line, "Vertical axis: dimensionless ratio, 0 to 1 |
  Horizontal axis: simulated time, the same window as above", which duplicates
  its axis titles the same way the compartment chart's does.

The four paragraphs `PL-6580` names total 995 characters, so **873 of the
1,868 characters of explanatory paragraph — 47% — survive the item that was
filed to remove them**, and no item names the remainder.

**Why it matters.** `PL-6580` closing is what will read as "the prose was
dealt with", and the largest single block on the screen will still be there.
An item that discharges the owner's ruling in name while leaving 40% of what
the ruling was about is worse than no item, because it retires the finding
without retiring the problem — and the next time the screen is looked at, the
remaining prose reads as prose that survived review and was therefore approved.

**Decision needed — ANSWERED 2026-09-13, see below.** For each of the three wash-in sentences below: delete,
reduce to a label or axis title, or keep. The owner decides; a session cannot,
because the disagreement is between two of the owner's own positions — the
2026-09-05 ruling on the reader, and the standing argument in
`_build_wash_in_section`'s docstring for correcting an expectation at the point
of display.

**Why this is a decision and not a scope widening.** The wash-in prose is
argued for in the code. `_build_wash_in_section`'s docstring states the case:
"The prose is not decoration. This is the graph the uptake literature is taught
from, so it arrives carrying a reader's expectations about what it means, and
three of those have to be corrected at the point of display rather than in a
document." That argument is not the same one `PL-6580` overturns. `PL-6580`
answers "does this reader need MAC explained" — no. This one asks "does this
reader expect F_A/F_I to mean something this model does not do" — and for the
denominator specifically the answer is plausibly yes, because the residents
this teaches learned the curve with F_I as the vaporizer dial, and here it is
the circuit.

The decision is per-sentence, and there are three:

1. **F_I is the modelled inspired concentration, not the dial.** Corrects a
   wrong reading a specialist reader will otherwise make. Strongest case to
   keep — but it is a fact about an axis, and an axis label ("F_A/F_I, F_I =
   modelled circuit") may carry it in six words rather than 346 characters.
2. **The curve is the textbook one only while inspired is held constant.** The
   chart already marks every setting change with a vertical rule and the panel
   beside it says which setting changed. Whether the sentence adds anything to
   the marks is the question.
3. **Modelled, not measured.** Required by the safety standard; the question is
   only whether a label carries it, as `_mac_reference_text` does for the MAC
   convention.

**Decide with the panel stripped**, as `PL-6580` says of its own axis-title
question — after that item lands, with the chart in front of you, not in
advance.

**Done when.** Each of the three sentences is either deleted, or reduced to a
label or axis title, or kept with the reason recorded in the docstring; and the
wash-in axis-key line is gone or justified against its axis titles.

## Answered 2026-09-13 (project owner), per sentence

786 characters of italic paragraph and a 108-character axis key become two
labels totalling about 145 characters. Nothing the safety-critical standard
requires left the screen; what left is the argument for it.

1. **F_I is the modelled inspired concentration, not the dial — reduced.** The
   heading carries the denominator now: "Wash-in: F_A/F_I, alveolar as a
   fraction of the modelled circuit". The correction a specialist arrives
   needing — that it is *not* the dial — is the first half of the one label
   under it.
2. **The curve is the textbook one only while inspired is held constant —
   reduced into the same label**, because the two are one fact. F_I is a
   denominator that moves, so the label reads "F_I = modelled circuit, not the
   vaporizer dial — a rise across a control mark can be the denominator
   moving, not uptake". Stated as a reading rule rather than a caveat, which
   is what a reader can act on.
   **Deliberately not folded into `_build_control_mark_legend_item`**, which
   was the obvious home and is wrong: the compartment chart shares that entry,
   and there a rise across a mark really is the agent going up, with no
   denominator to mistake it for. The warning is specific to the ratio.
3. **Modelled, not measured — kept, and moved to a line of its own.** Three
   words the standard requires, sitting at the end of a 440-character
   paragraph, are three words nobody reads. It now matches the control
   timeline's "Settings only — not a measurement."

**The axis key is deleted.** "Vertical axis: dimensionless ratio, 0 to 1"
restated the chart's left axis title and "Horizontal axis: simulated time" its
bottom one. Its one non-restating clause, "the same window as above", is true
by construction rather than by assertion: `_apply_time_base` computes one
window per frame and writes both charts' `min_x` and `max_x` from it.

**A fourth deletion the item did not list, and the reason it is safe.** The
rest of the second paragraph — the trace stopping where no agent has reached
the circuit, and ending on the equilibrium line past which the patient is
returning agent — is already said by `_format_wash_in_state`, live, naming
which of the two boundaries the trace stopped at *at the moment it stops*. A
message at the moment of need is strictly better than a standing sentence
saying it might happen, which is the distinction `PL-6580`'s own test draws.

**One earlier assertion was deliberately removed, so it is recorded rather
than quietly dropped.** `test_the_wash_in_plot_says_what_its_denominator_is`
asserted "no dead space" was on screen — the model-structure justification for
why circuit *is* inspired here. That justification is now `docs/MODEL.md`
§ "F_A/F_I as a displayed ratio"'s alone, which states it as "an assumption of
this circuit model rather than a general fact". It explains why the label is
true; the label is what a reader needs to read the plot. The test now asserts
the denominator-moving rule in its place.

**`docs/MODEL.md` needed no edit, and that was checked rather than assumed.**
§ "Minimum displayed outputs" requires the ratio to be "labelled as a ratio
against the modelled inspired concentration rather than against the vaporizer
dial, carrying the control marks above, ruled at the equilibrium the curve
approaches, and stating where it is not defined". All four still hold, by
label rather than by paragraph.

**Tests.** `test_nothing_between_the_wash_in_heading_and_its_plot_is_a_sentence`
applies `PL-6580`'s own rule to the panel below it — no string above the plot
contains ". " or ends with one, `_wash_in_state_text` exempt by identity — and
asserts the two labels the standard requires are present and the axis key is
gone.

**`touches` widened after the fact, and why rather than quietly.**
`tools/contrast_check.py` carried a WCAG requirement citing
`_wash_in_time_axis_caption` by name, so deleting the caption left that
requirement pointing at a symbol nothing defines and
`test_every_requirement_names_a_symbol_that_exists` failed. The citation now
names the one axis description that remains and records where the other went.
Declared here rather than left for `docket verify` to find outside the
commission: it is this item's own consequence, not new work.
