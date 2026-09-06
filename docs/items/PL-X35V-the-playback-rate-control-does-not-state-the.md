---
id: PL-X35V
title: The playback-rate control does not state the control resolution its rung costs, so the PL-NBWP disclosure reaches only a reader who has docs/MODEL.md open
status: untriaged
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
