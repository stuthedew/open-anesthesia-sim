---
id: PL-JVHL
title: The hover answers for whichever run is marginally nearer, so a 2 px hand movement silently swaps which run's value is read
priority: P1
effort: M
status: ready
classes: safety, ux
feature: scenario-branching
touches: src/anesthesia_sim/app/chart_frame.py, docs/MODEL.md, tests/unit/test_chart_frame.py
added: 2026-09-17
verify: grep -q 'def test_a_small_pointer_movement_never_swaps_which_run_the_hover_answers' tests/unit/test_chart_frame.py
---

**Problem.** The hover answers for whichever run is marginally nearer, so a 2 px hand movement silently swaps which run's value is read

`nearest_trace_point` and `nearest_wash_in_point` loop over every run on the
frame and keep the single globally nearest drawn point within
`HOVER_RADIUS_PIXELS` (12 logical px). With two runs on one axis the two runs'
points for the *same* compartment are frequently both inside that radius, so
which run answers is settled by arithmetic finer than a reader's hand — and
nothing in the box says which one won.

**Measured 2026-09-17**, reference adult on sevoflurane, trunk held at 1 MAC,
branch forked at 10 min, 60 min axis at 900 px wide and `theme.CHART_HEIGHT`
(360 px) tall, so 4.00 s/px and 0.0167 %/px. Share of the shared axis where
both runs' points for one compartment sit inside the 12 px radius, and share
where moving the pointer 2 px flips which run answers:

| Branch's management at the fork | Compartment | Both in radius | 2 px flips the run |
| --- | --- | ---: | ---: |
| doubled to 2 MAC | alveolar | 1.6% | 1.2% |
| doubled to 2 MAC | fat | 100% | 99.9% |
| raised to 1.25 MAC | alveolar | 8.5% | 8.4% |
| raised to 1.25 MAC | fat | 100% | 99.9% |
| vaporizer off | alveolar | 1.6% | 1.2% |
| vaporizer off | fat | 100% | 75.4% |

The fat row is 100% in every case, including against the widest management
difference available, because the percent axis is scaled by the alveolar peak
and the slow compartments are compressed near zero. The slow compartments are
what the chart exists to teach.

**Why it matters, and why it is consequential rather than cosmetic.** Of the hovers that could answer
for either run, the share that would print *different* text is 83.3–95.3%
(alveolar) and 43.8–81.4% (fat). Worked case, vaporizer off, fat at 3492 s:
`0.03%   0.02 ×MAC` or `0.01%   <0.01 ×MAC` depending on a 2 px movement — a
threefold difference in stored fat concentration between a run still carrying
agent and one 48 minutes into emergence.

**Not the same problem as `PL-MN4J`.** `PL-MN4J` decides whether the box
*names* the run. Naming it makes this flip visible rather than silent, which
is a large mitigation and the reason both sit under `scenario-branching` — but
it does not
make the hover answer for the curve the reader aimed at. That wants a
targeting rule: prefer the run whose curve the pointer is nearest along its
length, or require the pointer to be inside a run's own band, rather than
taking a global minimum over a set the reader cannot see.

**Where.** `src/anesthesia_sim/app/chart_frame.py` (`nearest_trace_point`,
`nearest_wash_in_point`); `docs/MODEL.md` § "The chart's hover readout".

**Found 2026-09-17** while measuring the case for `PL-MN4J`. Filed rather than
fixed: the fix is a change to the targeting rule, which that section derives,
and `CLAUDE.md`'s fix-now door admits neither a new test nor a decision.

**Done when.** A pointer movement of a few pixels cannot change which run the
hover answers for while both runs' points stay inside `HOVER_RADIUS_PIXELS` -
by preferring the run whose curve the pointer is nearest along its length, or by
requiring the pointer to be inside a run's own band, whichever the targeting
work settles on - a test in `tests/unit/test_chart_frame.py` drives the two-run
fat-compartment case that measures 100% ambiguous today, and `docs/MODEL.md`
§ "The chart's hover readout" states the rule the reader can rely on.
