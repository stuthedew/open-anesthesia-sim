---
id: PL-X35V
title: The playback-rate control does not state the control resolution its rung costs, so the PL-NBWP disclosure reaches only a reader who has docs/MODEL.md open
priority: P1
effort: M
status: needs-decision
classes: safety, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/playback.py, src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/simulation_view.py, tests/unit/test_formatting.py, tests/unit/test_playback.py, tools/contrast_check.py
added: 2026-09-06
---

**Problem.** `PL-NBWP` established that a setting changed while the run plays
first acts at a tick boundary, so the reachable simulated instants are
`multiplier x 0.1` s apart - 0.1 s at 1x and 30 s at 300x - and that one grid
step of that displaces a displayed compartment by up to about 10 pp at 300x on
an abrupt manoeuvre. It corrected the three places that stated the tolerance
without naming the rate: `app/playback.py`, `core/uptake_system.py`'s
`MAXIMUM_SIMULATION_STEP_S` comment, and `docs/MODEL.md` § "Supported
simulation step". All three are documents. The interface says nothing.

**Why it matters.** The reader who needs this is the one dragging a slider at
300x, and they do not have the model document open. `CLAUDE.md`'s
safety-critical standard asks that model limitations be made visible rather
than left for polished output to imply away, and
`.claude/rules/expert-review.md` prefers an interface that prevents an error
over one that warns after it - so a disclosure that lives only in prose is the
weakest form of the fix that was available. The rate dropdown is the exact
moment the reader chooses the resolution, which makes it the one place the cost
can be stated without being a warning nobody reads.

**What it is not.** Not a behaviour change. `PL-NBWP` settled that the grid
stays where it is, on the measured ground that frames are two grid steps apart
at every rate, so a finer grid would resolve control timing the display cannot
show. This item is about what the reader is told, and it should not reopen
that.

**Decision needed.** Where the interface states the control-resolution cost
of a rate, and what that does to `format_playback_rate`'s single-source
property. The three candidates below are not equivalent in cost or in
intrusiveness, and the second half of the question cannot be dodged: the
cheapest candidate changes a function that deliberately serves both the
control that sets the rate and the mode line that reports it, so either both
gain the disclosure - a judgment, not a side effect - or that function forks
and gives up the property its docstring argues for. Answering this is the
work; the drawing is not.

**Approach, to be confirmed rather than assumed.** Candidates, cheapest first:
state the grid in the rate's own label, so 300x reads as its resolution as well
as its speed; or a line under the control that changes with the selection; or -
the strongest and the most intrusive - surface it only once the reader moves a
control at a rate above 1x, which is the only moment it is actionable.

**The first has a complication worth knowing before starting.**
`format_playback_rate` renders `"{multiplier}x real time"` and is deliberately
*one* function for both places the rate appears - the control that sets it and
the line under the clock that reports it - "so the two cannot state the same
mode differently". Lengthening it therefore lengthens both, and the line under
the clock is a mode indicator rather than a place to teach a tolerance. So
either the disclosure is wanted in both places, which is a judgment to make
rather than a side effect to accept, or that function has to gain a second
form and give up the single-source property its docstring argues for. That
tension is the design work in this item; the drawing is not.

Whether a dropdown row has the width for it is the next question, and
`app/theme.py` and `.claude/rules/ui-color.md` govern anything drawn.

**Where.** `src/anesthesia_sim/app/playback.py`'s `SUPPORTED_PLAYBACK_RATES`,
which now carries the grid per rung in its comment;
`src/anesthesia_sim/app/formatting.py`'s `format_playback_rate`, which is where
a rate becomes a label; the rate control in
`src/anesthesia_sim/app/simulation_view.py`; and
`tests/unit/test_formatting.py` beside whatever the label becomes.

**Sequenced after `PL-NBWP` and independent of `PL-ZVS7`.** `PL-NBWP` supplies
the numbers and has landed; `PL-ZVS7` pins them with a regression test and
neither blocks the other.

**Done when.** A reader who has never opened `docs/MODEL.md` can tell, from the
interface alone and at the moment they select a rate, that a control change at
that rate is resolved to `multiplier x 0.1` simulated seconds - and a test holds
the displayed text to the same ladder
`test_the_control_grid_at_each_rate_is_the_one_two_documents_publish` holds the
model to, so a rung cannot be added with a label that understates it.

## Design round, 2026-09-06 - the question narrowed, and half the work landed

**The dilemma this item calls the design work has a third horn, and taking it
costs nothing.** The brief above frames the choice as: either both places the
rate appears gain the disclosure, or `format_playback_rate` forks and gives up
the single-source property its docstring argues for. Neither is necessary. What
that property protects is that the two sites cannot state the same *mode*
differently - not that they render the same string. A second renderer that
*contains* the first (`f"{format_playback_rate(m)} - {format_control_grid(g)}"`)
keeps the guarantee as a substring relation, which is stronger than "one
function" because it is directly assertable in a test. So the fork is available
without the loss if a later answer wants it, and it is not an argument against
any candidate.

**Withdrawn on the project owner's challenge, 2026-09-06 - see the section
below.** Recorded as it stood: the second candidate, built as the control's own
caption rather than as a new layout element. `ft.Dropdown` in the shipped Flet 0.86.5
carries `helper_text` and `helper_style` (verified against
`dataclasses.fields`), so the line under the control is three lines of view
code and no restructuring of the transport row. `format_playback_rate` is then
untouched, the mode line under the clock stays a mode indicator, and the
disclosure sits where a reader is when they choose the resolution and is still
there when they reach for a slider.

**Why not the first candidate.** Putting the grid in the option text is the
only one that prices the trade-off at the moment of *comparison*, which is a
real advantage and the reason it is worth re-raising later. But the closed
`ft.Dropdown` renders the selected option's own text at `width=150`, so
`300x real time - 30 s control grid` truncates there, and a truncated safety
disclosure is worse than none. Fixing that means widening the control to about
270 px in a wrapping row that already holds an agent dropdown, three buttons
and the status word. `menu_width` widens the open menu only and does not help
the closed field.

**Why not the third.** A message raised once the reader moves a control at a
rate above 1x is a warning after the fact, and
`.claude/rules/expert-review.md` prefers an interface that prevents an error
over one that warns after it. It is also transient, fires repeatedly through a
drag, and carries the most state and the most test surface of the three.

**Three wording constraints found while looking, and they bind whichever
placement wins.**

- **Never "step".** The simulation step is 0.1 s at every rate and the module
  docstring calls holding that "the safety property this module exists to
  hold". A caption reading `30 s steps` at 300x asserts the opposite of it.
- **Never "delay", "lag" or "late".** `docs/MODEL.md` states that nothing
  arrives late: the recorded `ControlChange.elapsed_s` and the step the setting
  acts over agree at every rate. What coarsens is which instants can be
  *chosen*.
- **The unit is simulated seconds and the caption must say so.** At 300x, 30
  simulated seconds is 0.1 real ones. A reader taking the number as real time
  has the cost wrong by the multiplier itself.

`0.1 s` is stated at 1x rather than suppressed, for the reason
`format_playback_rate` renders `1x real time` rather than nothing: an absent
line makes the line's presence the signal.

**Contrast costs nothing here.** `MUTED` is already declared against both
`PANEL` and `BACKGROUND` at the 4.5:1 normal-text minimum in
`tools/contrast_check.py`, so a `MUTED` caption amends an existing entry's
prose to name the new site and adds no pair.

**What landed in this round, being the same under all three answers.**

- `PlaybackRate.control_grid_s(...)` in `app/playback.py`, deriving the
  interval through `steps_per_tick` so it inherits that method's refusals
  rather than re-deriving them, with a docstring naming what the number is not.
- `format_control_grid(...)` in `app/formatting.py`, rendering the magnitude
  alone and refusing an interval one decimal would understate rather than
  publishing a shorter one.
- `test_the_control_grid_at_each_rate_is_the_one_two_documents_publish` now
  reads through `control_grid_s`, so the published ladder and the shipped
  derivation of it are one assertion instead of two that could drift.

**What is still open, and is the whole of what remains.** Where the string goes
and what it says. No `verify:` command is written yet, deliberately: the
command has to name the test on the interface path, and which path that is is
the open question.

## Challenged and re-derived, 2026-09-06 - the number should not be displayed

The project owner asked what a caption stating the grid would mean to a
reader, and why it needs displaying at all. Two facts checked against the
source say the brief's premise is half wrong, and they were not in the brief.

**The control grid is finer than the display, by exactly two, at every rate.**
`RENDER_INTERVAL_S` is `2 * SIMULATION_TICK_INTERVAL_S`
(`app/simulation_view.py`), so a frame is two grid steps: at 300x the reader
sees simulated time in 60 s increments and can act on it in 30 s ones.
`docs/MODEL.md` § "Supported simulation step" states this as the reason
`PL-NBWP` left the grid alone. It has a consequence that item did not draw:
a reader cannot check `30 s` against anything on screen, and cannot act on the
difference between 30 s and the 60 s they can see. The rate label is
displayable precisely because it *is* checkable against the clock
(`format_playback_rate`'s docstring makes that the argument for it); a grid
figure has the opposite property.

**The 10 pp figure is not the learner's manoeuvre.** It is a ventilator start
at the envelope corner. The ordinary action - open the dial, or close it -
reaches 1.5 pp at 300x, and the transient saturates rather than scaling.

**So the number and the fact separate, and only one of them is worth screen
space.** The *number* is uncheckable, imperceptible and unactionable. The
*fact* - that a setting cannot be placed at a chosen instant while the run is
playing above 1x, and that pausing gives exact timing - is invisible to a
reader precisely because the display is coarser than the grid, which is what
makes it worth disclosing rather than leaving to be discovered. It is also a
teaching affordance rather than a warning: nothing on screen currently tells a
reader that timing a manoeuvre is something this simulator can do at all, and
`docs/MODEL.md` names pause-change-resume as the exact route at every rate.

**Revised recommendation.** Say the actionable half in words and drop the
figure - a line reading approximately "Time advances in jumps while playing;
pause to change a setting at an exact moment." `docs/MODEL.md` keeps the
ladder for a reader who wants it. Dropping the item outright is the honest
alternative and is not a weak one; building it as the brief describes is the
weakest of the three, because it spends the interface's scarcest resource on
the half a reader can neither verify nor use.

**If the figure is dropped, `format_control_grid` loses its only production
caller** and should come out with it; `PlaybackRate.control_grid_s` stays,
because `test_the_control_grid_at_each_rate_is_the_one_two_documents_publish`
reads the published ladder through it.

**Filed while here:** `PL-SR8F`, on `docs/MODEL.md` calling the case-opening
displacement "two orders milder at every rate" when the figures in the same
sentence are 0.8 to 1.3 orders apart.
