---
id: PL-F9TQ
title: PL-6580 strips only the concentration chart, but the wash-in panel's two paragraphs are the largest standing prose block on the screen and no item covers them
priority: P2
effort: S
status: needs-decision
classes: ux
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py
added: 2026-09-08
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

So roughly 40% of the standing prose survives the item that was filed to
remove it, and no item names the remainder.

**Why it matters.** `PL-6580` closing is what will read as "the prose was
dealt with", and the largest single block on the screen will still be there.
An item that discharges the owner's ruling in name while leaving 40% of what
the ruling was about is worse than no item, because it retires the finding
without retiring the problem — and the next time the screen is looked at, the
remaining prose reads as prose that survived review and was therefore approved.

**Decision needed.** For each of the three wash-in sentences below: delete,
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
