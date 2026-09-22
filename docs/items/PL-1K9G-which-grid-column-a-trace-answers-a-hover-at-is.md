---
id: PL-1K9G
title: Which grid column a trace answers a hover at is decided in two dimensions, so a purely vertical 2 px move can change the instant a value is labelled with
priority: P1
effort: M
status: done
classes: safety, ux
feature: compartment-trace-legibility
touches: src/anesthesia_sim/app/chart_frame.py, docs/MODEL.md, tests/unit/test_chart_frame.py
added: 2026-09-20
closed: 2026-09-22
pr: 912
payoff: two compartments of one run stop being labelled with two different instants in one hover box, so a reader comparing them is comparing one moment
verify: grep -q 'def test_every_compartment_of_one_run_answers_at_one_instant' tests/unit/test_chart_frame.py
---

**Problem.** Which grid column a trace answers a hover at is decided in two dimensions, so a purely vertical 2 px move can change the instant a value is labelled with

**Found 2026-09-20 while closing `PL-0RZ0`** (the hover's compartment flip),
and not fixed there: it is a different mechanism, its own decision, and the
fix-now door admits neither a new test nor a decision.

`nearest_trace_point` keeps each `(run, compartment)`'s nearest drawn point by
`_pixel_distance`, which composes the time and percent axes. So where two grid
columns are near-equidistant in time, the pointer's *height* decides which of
them a trace answers at - and a 2 px move up or down can change the instant on
a value line while the value itself is unchanged. Observed on the branched
sevoflurane case at t = 1200 s: muscle answers at 19m56s and fat at 20m for the
same run under one pointer, and moving the pointer 2 px up moves muscle's line
to 20m.

**Why it is probably not the same defect.** `PL-0RZ0`'s failure was that the
box named a different *trace* - a value under the wrong label. Here the label
is right, the compartment is right, and only the instant moves, by one grid
column: 4 s on the 60-minute axis, 48 s on the 12-hour one. The value at the
two columns is usually equal to the displayed precision, which is why nothing
had noticed.

**Why it may still be one.** Across a control event or a steep kink, two
adjacent columns can differ by more than the displayed resolution, and then a
vertical hand movement changes a printed concentration with nothing in the box
moving except the instant - which is exactly the shape `PL-JVHL` and `PL-0RZ0`
both closed. Nobody has measured how often two adjacent drawn columns differ by
at least one displayed digit, and that measurement is the first step here
exactly as it was in `PL-0RZ0`.

**The obvious candidate fix, and its cost.** Choose the column by time alone -
the pointer names an instant, the trace answers at its nearest drawn instant -
and keep the pixel radius for deciding whether the trace answers at all. That
makes the instant a function of the pointer's x position only, which is what a
reader would predict. It would change which point some hovers report, so it
wants the same before-and-after scan `PL-0RZ0` ran rather than an argument.

**Why it matters.** Two compartments of one run can be labelled with two
different instants inside one hover box, so a reader comparing muscle against
fat "at the same moment" is comparing 19m56s against 20m. `CLAUDE.md`'s
safety-critical standard counts that as a presentation failure in its own
right - the correct number with the wrong patient context - and across a
control event or a steep kink the concentration itself can move by more than
the displayed resolution under a purely vertical hand movement, which is the
shape `PL-JVHL` and `PL-0RZ0` both closed.

**The class is provisional on a measurement nobody has run, and that is stated
rather than assumed.** This is triaged `defect, ux` at `P2` because the value
at two adjacent columns is usually equal to the displayed precision, which is
why nothing had noticed. How often two adjacent drawn columns differ by at
least one displayed digit has not been counted. That count is this item's first
step, and a non-trivial answer reclassifies it `safety` at `P1` - at which
point it re-enters the current gate unconditionally under § "The cadence"
rather than sitting in the deferral written for it. Do not treat the present
class as a finding about the hazard; it is a finding about what has been
measured.

**Done when.** The count above has been run and recorded; and either the column
a trace answers at is a function of the pointer's x position alone - with the
pixel radius kept for deciding whether the trace answers at all - or the item
records why composing both axes is right, with the before-and-after scan
`PL-0RZ0` ran rather than an argument; and a test under
`tests/unit/test_chart_frame.py` holds that every compartment of one run
answers at one instant.

## Measured 2026-09-22: the count is not trivial, so this is `safety` at `P1`

`PL-0RZ0`'s geometry, rebuilt: reference adult on sevoflurane, the trunk at
1 MAC with its dial raised by half at 10 minutes and run to 20; branches forked
at 10 minutes under the same three managements (doubled to 2 MAC, raised to
1.25 MAC, vaporizer off), each run 10 minutes; a 60-minute axis 900 px wide
and 360 px tall, so 4.00 s/px and 0.0167 %/px, and the shipped 12 px radius.
Two cases were added because the chart is steepest where a dial change is a
near-vertical step: a two-hour single run (1 MAC, raised by half at 10 min,
vaporizer off at 60 min) on its fitted 2-hour axis (8 s/px) and on the 12-hour
one (48 s/px). The scan walks every pixel of height at four sub-pixel phases
per pixel column, so nothing below is an artefact of where the anchored grid
falls against the pixel grid, and its selection was held against
`nearest_trace_point` itself at 400 random pointer positions per case, with no
mismatch, before any number was kept.

**The count this item's first step asked for.** Adjacent drawn columns whose
value line prints differently (`_hover_value`: percent and ×MAC):

| Trace | one run, 60 min | branches, 60 min | 2 h axis | 12 h axis |
| --- | ---: | ---: | ---: | ---: |
| Circuit | 54.7% | - | 23.8% | 50.3% |
| Alveolar | 67.0% | 44.0-80.7% | 31.0% | 60.9% |
| Mixed venous | 68.0% | 46.0-85.3% | 35.7% | 69.5% |
| Vessel-rich | 77.0% | 57.3-93.3% | 36.7% | 65.6% |
| Muscle | 9.7% | 3.3-16.0% | 15.3% | 67.5% |
| Fat | 1.0% | 0.7-1.3% | 0.9% | 6.0% |

So the premise the `P2` class rested on - that the value at two adjacent
columns is usually equal to the displayed precision - holds for fat and mostly
for muscle, the pair the observation above happened to be made on, and is false
for the other four. By this item's own rule that reclassifies it `safety` at
`P1`. It is already on v0.6.0's frozen list (`ROADMAP.md`, the product lane
cleared before the milestone begins), so the reclassification changes its rank
and not its gate.

### Before: the shipped rule

Two or more readings of one run in one box, and how often they carry different
instants:

| Chart | Compartments | 2+ readings of one run | of those, mixed instants | of mixed, digits differ | spread, median / max |
| --- | --- | ---: | ---: | ---: | ---: |
| one run, 60 min | all six | 31.7% | 70.1% | 91.9% | 16 s / 72 s |
| two runs, 60 min | muscle + fat | 71.0-72.8% | 13.0-16.8% | 11.6-19.0% | 4 s / 4 s |
| two runs, 60 min | mixed venous + vessel-rich | 18.9-32.7% | 88.3-94.7% | 95.7-98.8% | 12-16 s / 32-52 s |
| two runs, 60 min | alveolar + fat | 1.6-6.4% | 74.0-91.5% | 65.3-100% | 4-16 s / 40 s |
| one run, 2 h axis | all six | 38.2% | 54.5% | 83.6% | 32 s / 176 s |
| one run, 12 h axis | all six | 57.5% | 84.5% | 97.5% | 288 s / 912 s |

"Digits differ" is the share whose compartments print differently at one
shared instant than at the instants the box gave them - the mismatch a reader
could see. **The spread is the correction the record needed**: the premise
above, `HoverReading`'s docstring and `docs/MODEL.md` all said one grid column.
The nearest point in two dimensions on a sloped trace can be as far to the side
as the radius reaches, so the measured spread is up to 18 columns on the
60-minute axis and 19 on the 12-hour one - fifteen minutes between two values
one box presents together.

A purely vertical 2 px movement, of the pairs where one trace answers at both
ends:

| Chart | Compartments | instant moves | printed value moves | largest shift | largest change |
| --- | --- | ---: | ---: | ---: | ---: |
| one run, 60 min | all six | 44.9% | 35.1% | 40 s | 0.13 pp |
| two runs, 60 min | muscle + fat | 3.0-5.4% | 0.3-0.8% | 4 s | 0.001 pp |
| two runs, 60 min | mixed venous + vessel-rich | 50.6-62.8% | 36.9-52.8% | 8 s | 0.02 pp |
| two runs, 60 min | alveolar + fat | 34.2-42.4% | 25.8-35.6% | 24 s | 0.09 pp |
| one run, 2 h axis | all six | 25.5% | 19.7% | 96 s | 0.24 pp |
| one run, 12 h axis | all six | 37.3% | 33.3% | 672 s | 0.39 pp |

The wash-in plot measured its distance the same way. One trace per run, so no
box there could mix one run's instants, but the same vertical movement moved
its instant on 23.9-44.4% of pairs across these cases and its printed ratio on
7.7-20.6%.

### After: the pointer names the instant

Each run answers at its drawn instant nearest the pointer in time, ties to the
earlier, and each of its traces answers there if that point is inside the
radius; on the wash-in plot a run's stretches are one set of drawn instants.
Measured on the same cases:

- **Mixed instants in one run's readings: none**, and a vertical movement moves
  no instant and no printed value, on either plot.
- **It answers nowhere the shipped rule did not.** Its answers are a subset: a
  point inside the radius at the pointer's instant was inside it before.
- **No drawn instant becomes unreachable.** Every one is answered from
  somewhere at the four sub-pixel phases, on both plots and every case. At
  whole-pixel pointer positions only, one control-event column on the 12-hour
  axis - 1 of 151 - falls exactly half a pixel between two grid columns and is
  answered only from a half-pixel position; its state is continuous with its
  neighbours', so its printed value lies between theirs.
- **The area a trace answers over shrinks where it is steep**, and this is the
  cost. Of the area each trace answered over, the share it still answers over:
  on the 60-minute and 2-hour axes 84-85% for circuit, 85-98% for alveolar,
  88-98.5% for mixed venous and vessel-rich, and 99.8-100% for muscle and fat;
  on the 12-hour axis 45-54% for the four fast compartments, 93% for muscle and
  100% for fat. What is lost is the pointer beside a steep segment answered
  from a point level with it - up to 12 px, and on the 12-hour axis up to ten
  minutes, from the instant the pointer names. The wash-in plot keeps 77-92% on
  the shorter axes and 65% on the 12-hour one.

What a reader sees change, as a share of the positions the shipped rule
answered:

| Chart | Compartments | identical | same traces, instant moved | of which a value moved | a trace stops answering | nothing answers |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| one run, 60 min | all six | 27.5% | 63.0% | 48.4% | 9.5% | 4.6% |
| two runs, 60 min | muscle + fat | 75.9-80.8% | 19.1-24.0% | 2.2-4.7% | 0.1% | 0.1% |
| two runs, 60 min | mixed venous + vessel-rich | 12.6-14.0% | 76.2-80.0% | 68.6-70.5% | 7.3-11.1% | 2.9-4.3% |
| two runs, 60 min | alveolar + fat | 34.9-43.1% | 50.7-56.8% | 37.9-43.8% | 6.2-9.4% | 4.5-7.0% |
| one run, 2 h axis | all six | 51.7% | 37.9% | 21.6% | 10.3% | 3.5% |
| one run, 12 h axis | all six | 16.0% | 35.2% | 26.4% | 48.8% | 22.5% |

**Why the radius is measured at the named instant, and not to any of the
trace's points.** Keeping the shipped rule's reach and reporting the point at
the named instant is the other way to make the instant a function of the
pointer's time alone, and it keeps every answer the shipped rule gave. It was
measured and refused: wherever the chosen rule declines, it would report a
point a median 13.5 px and up to 42.5 px from the pointer on the 60-minute
single-run chart, and up to 146 px on the 12-hour axis - the dot and the box
hung on a value the reader is nowhere near, presented as the one under the
pointer. The chosen rule keeps the invariant that every value reported is
within the radius of the pointer *and* at the instant it names, at the price
of the steep-segment area above.

## Landed 2026-09-22

`nearest_trace_point` finds each run's drawn column nearest the pointer in time
once (`_nearest_column`, one bisection, a tie to the earlier column) and asks of
every visible compartment only whether its point there is inside the radius.
`nearest_wash_in_point` does the same over a run's stretches taken together
(`_nearest_wash_in_point`, a tie to the earlier stretch, which is also where a
column drawn twice as two stretches' shared end is read from). `_keep_nearest`
and `_columns_within` went with the rule they served. The readout's forms are
unchanged: every line still states its instant, because two runs can still
differ - each draws its own control-event columns and a branch draws nothing
before its fork - and within one run the lines now always agree.

The scan was re-run against the shipped functions after the change: the time
rule's selection matched `nearest_trace_point` at 400 random pointer positions
in every case and `nearest_wash_in_point` at 300 per run, with no mismatch.

**The wash-in plot is in this change although the item's payoff names only the
compartment chart.** It measured its distance in the same two dimensions, so
the title's mechanism - a vertical move changing the instant a value is
labelled with - was live there too, on 23.9-44.4% of movements; leaving it
would have given the two plots different hover rules for one gesture.

Tests: `test_every_compartment_of_one_run_answers_at_one_instant` (the geometry
reduced to a flat and a steep trace, held against the retired rule's split),
`test_a_vertical_hand_movement_never_moves_the_instant_a_hover_reports` (real
one- and two-run frames swept across the dial change and the live end),
`test_a_trace_answers_only_where_its_point_at_the_named_instant_is_in_reach`
(the radius measured at the named instant, which is what refuses the
alternative above), `test_the_wash_in_hover_answers_at_the_instant_the_pointer_names`
and `test_a_run_that_draws_no_instant_answers_no_hover_and_silences_no_other`
(the empty-run branch the bisection needs). All five of the first failed
against the shipped rule on the instant itself before the change.

**Documentation swept:** `docs/MODEL.md` - § "Where more than one trace
answers" (the instant rule, its measurement and its cost, replacing the
paragraph that called per-line instants required because compartments did not
share one), the implementation paragraph's provenance line, the hazard table
(the compartment row's wording, and a new row for reading one run's readings as
one moment), and one sentence in § "The hover and the run it belongs to" that
still described the pre-`PL-JVHL` rule in the present tense;
`src/anesthesia_sim/app/chart_frame.py` docstrings (`HoverReading.time_s`,
`nearest_trace_point`, `nearest_wash_in_point`, `format_compared_trace_hover`).
Checked and left as they stand: `README.md`'s hover bullet, `docs/ARCHITECTURE.md`'s
`chart_frame` entries and `src/anesthesia_sim/app/qt_chart.py`'s hover
docstrings, all of which describe what answers without describing how the
point is chosen; and `ROADMAP.md`'s v0.5.0 deferral of this item, which records
what had been measured then.
