---
id: PL-FPY2
title: A wrapped mark row's continuation can be a whole clause naming a run, so it reads as a row of its own and binds to the wrong mark
priority: P2
effort: M
status: done
classes: defect
feature: two-run-attribution
milestone: v0.5.5
touches: src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/theme.py, tests/integration/test_simulation_view.py, tools/glyph_check.py
added: 2026-09-20
closed: 2026-09-22
pr: 905
payoff: stops a wrapped standing clause reading as a row of its own and attaching one run's answer to the wrong mark
verify: grep -q 'def test_a_wrapped_mark_row_is_told_apart_from_the_row_below_it' tests/integration/test_simulation_view.py
---

**Problem.** A wrapped mark row's continuation can be a whole clause naming a run, so it reads as a row of its own and binds to the wrong mark

**Why it matters.** `MarkListing.text` joins the rows with `\n` into one
`QLabel` with `wrap=True` (`qt_widgets.py`'s `MarkListingLabel`), so a row that
wraps continues at column zero with no bullet and no indent, and nothing
separates a continuation from the next row. Before `PL-LHBY` that was safe by
accident: the longest row a mark could draw ended in
`not reached within the supported run length`, whose continuation is a
fragment — `supported run length` — that cannot be read as a row of its own.
An attributed clause can be. Measured by the adversarial review of `PL-LHBY`
at a 350 px sidebar in the real 12 px font:

```text
MAC targets
Fat 1.25 ×MAC – saturation probe · Run 1 not yet ·
Run 2 reached
Alveolar 0.50 ×MAC · Run 1 reached · Run 2 not yet
```

`Run 2 reached` stands alone between two mark rows, and which compartment and
height each management got to is precisely what the comparison screen exists
to convey — so a row misread here is a wrong clinical reading of the
comparison, not a cosmetic one. The window opens at 0.8 of screen width with a
3:1 chart-to-sidebar split, so 300–380 px is the realistic range and rows wrap
across all of it.

**Amplifier.** A mark's label has no length bound: neither `time_label_edit`
nor `target_label_edit` sets `setMaxLength`, so there is no longest row. That
may be the cheaper half of the fix or a second item; decide it with the first.

**What it is not.** Not an argument against attributing the standings, which
is what `PL-LHBY` and `PL-4KZD` closed and what the comparison needs. It is
the listing's typography that assumed short rows.

**Done when.** A wrapped mark row is visually distinguishable from the row
below it — indented continuations, one label per row, or equivalent — and a
test pins it at the narrow end of the sidebar's real width range.

**Resolution, 2026-09-22.** Each mark is now a `MarkRow` of its own: a bullet
in a column of its own and the row's text beside it, so a continuation starts
under its own text, a bullet's width plus 6 px right of where the next row
starts, with 2 px between rows. `MarkListing.text` became `empty_line`, so the
choice between the rows and the empty line is still the frame's and the widget
still decides nothing. The length cap the amplifier raised was decided against:
the hanging indent removes the misreading at any length, and the sidebar
scrolls, so an unbounded name costs height rather than a wrong reading; a cap
would restrict the learner and fix nothing that is left. `U+2022` joined
`tools/glyph_check.py`'s confirmed list on an offscreen render in DejaVu Sans
at 12 px, looked at beside the middle dot the rows already use.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "Introduced by this milestone's own implementation work".

> **Two more from `PL-LHBY`'s own close-out, 2026-09-20**. Both defer by the presence rule's own terms rather than by the refilling-queue exception. "The gate is a snapshot" says that a finding "defers to the next gate only when the problem itself is new: introduced by work done while clearing this gate or implementing the milestone it protects". Both are properties of the attributed mark row that `PL-LHBY` created. `PL-FPY2` is the one to watch, and it is deferred with that said. When a row wraps, its continuation can now be a whole clause that names a run. A reader can then take the continuation for a row of its own, and bind one management's answer to the wrong mark. This was measured at a 350 px sidebar in the real 12 px font. It is declined only because the rows it affects are the ones that `PL-LHBY` made correct in substance. So the reading is harder rather than wrong. It is recommended as the first of the two taken off this list. `PL-08CR` is a `needs-decision` tidy-up. Since that same change, no production path calls two public row formatters. Their docstrings are already corrected, so nothing in the tree is misleading. The two: `PL-08CR`, `PL-FPY2`.
