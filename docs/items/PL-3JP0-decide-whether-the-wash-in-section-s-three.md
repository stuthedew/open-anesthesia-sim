---
id: PL-3JP0
title: Decide whether the wash-in section's three paragraphs survive the same test PL-6580 applied to the chart panel above it
status: untriaged
added: 2026-09-08
---

**Problem.** Decide whether the wash-in section's three paragraphs survive the same test PL-6580 applied to the chart panel above it

**Why it matters.** PL-6580 stripped everything between the compartment
chart's heading and its plot down to legend and labels, on the argument that
the reader is an anesthesia provider and the panel was teaching what they
already know. It deliberately did not touch the $`F_A/F_I`$ section below the
same plot, which still carries two italic paragraphs plus its own axis
caption — so the one panel now reads two ways depending on which half of it
you are looking at.

**But the case is not the same, and that is the question.** The chart panel's
prose explained MAC, MAC-awake and what a tissue compartment is: fundamental
knowledge for this reader. `_build_wash_in_section`'s docstring argues its
paragraphs do something different — the wash-in curve is the one graph the
uptake literature is taught from, so it arrives carrying a reader's
expectations, and three of those are wrong *for this model* rather than merely
unstated: which concentration the denominator is (the modelled inspired
fraction, not the vaporizer dial), that the curve is the textbook one only
while that fraction is held constant, and that the trace is bounded to the
wash-in domain and stops outside it. Correcting a false expectation an expert
brings with them is not the same act as defining a term they know.

**So the answer is plausibly "keep them", and that is a real outcome.** What
should not survive unexamined is the wash-in axis caption, `Vertical axis:
dimensionless ratio, 0 to 1 | Horizontal axis: simulated time, the same window
as above`: its left half duplicates the axis title `F_A / F_I` and the axis's
own 0-to-1 labels, which is exactly the duplication PL-6580 removed from the
caption above. The right half is not duplication — that the two plots share a
window is a claim neither axis makes.

**Done when.** Each of the two paragraphs is either kept with the reason
recorded, or removed with `docs/MODEL.md` § "F_A/F_I as a displayed ratio"
confirmed to carry the full statement; the axis caption is reduced to whatever
part of it no axis title states; and `make check` is clean.
