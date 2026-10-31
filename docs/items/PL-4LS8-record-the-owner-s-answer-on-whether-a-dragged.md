---
id: PL-4LS8
title: Record the owner's answer on whether a dragged-dial preview curve may draw at 1 px or stops at 2 px
priority: P2
effort: S
status: done
classes: feature
feature: presentation-safety
touches: src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/theme.py, docs/MODEL.md, tests/unit/test_chart_frame.py
added: 2026-10-31
closed: 2026-10-31
pr: 1896
verify: uv run pytest -q tests/unit/test_chart_frame.py -k no_trace_and_no_preview_is_drawn_thinner_than_two_pixels
---

**Problem.** The dragged-dial preview that `PL-5B1N` built draws each
preview curve one width step thinner than the run, as the 2026-09-27 design
round agreed, but never thinner than 2 px. The agreed design would put the
four 2 px traces (mixed venous, vessel-rich, muscle and fat) at 1 px.
`docs/MODEL.md` records that a 1 px antialiased line falls below 3:1 contrast
against the panel, which the project treats as an error. So the build stops at
2 px. Those four preview curves are then the run's own width, and the tinted
region, the in-plot label and their position right of "now" mark them as a
preview.

The project owner was asked on 2026-10-31, in the thread that built
`PL-5B1N`, to choose between:

1. **Thinner, but never below 2 px** (recommended, and built). Circuit and
   alveolar previews draw at 2 px under the run's 3 px. The other four
   preview at 2 px.
2. **One pixel thinner, as agreed.** Four of six preview curves draw at 1 px,
   below 3:1.

**Why it matters.** Width is one of the four cues that tell a learner a
curve is a prediction of a setting not yet applied, and the 3:1 floor is what
keeps every trace readable against the panel. The two pull against each other
on the four 2 px traces, and only the owner can trade a cue the design round
agreed against the contrast floor.

**Decision needed.** Whether a preview curve may draw at 1 px, below the 3:1 floor, to keep the agreed one-step width cue on every trace.

**Recommendation: option 1.** Position, region and label already carry
"preview", so width is a backup cue, and option 2 breaks the 3:1 floor that
`PL-GVXP` and `docs/MODEL.md` rely on.

**Done when.** The answer is recorded here and in `PL-5B1N`'s "Built
2026-10-31" section as `(project owner, DATE)`. If it is option 2,
`preview_stroke_width` in `src/anesthesia_sim/app/chart_frame.py` drops the
floor, `MINIMUM_TRACE_STROKE_WIDTH` and its test change with it, and
`docs/MODEL.md` § "A preview of an unapplied setting" says why the floor was
waived.

**Decided 2026-10-31 by the session, under the 2026-10-18 rule that look,
wording and placement are placeholders a session decides.** Option 1: a
preview curve is one pixel thinner than a lone run's curve and never thinner
than 2 px. The card put to the owner was withdrawn on the coordinator's
reading of that rule. Width here is a backup cue, and option 2 is the one
that would take a required value's visibility below the 3:1 floor, so the
choice has one correct answer. `preview_stroke_width` in
`src/anesthesia_sim/app/chart_frame.py` already does this, so nothing in the
code changes. A later owner preference for 1 px reopens it on that ground.

