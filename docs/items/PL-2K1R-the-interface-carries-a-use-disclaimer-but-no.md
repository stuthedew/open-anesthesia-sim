---
id: PL-2K1R
title: The interface carries a use disclaimer but no interpretation one, so nothing tells a reader the compartment readouts and chart traces are modelled rather than measured
priority: P1
effort: M
status: ready
classes: safety, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py, docs/MODEL.md
added: 2026-09-13
verify: uv run pytest tests/unit/test_simulation_view.py && grep -q 'def test_the_readouts_are_labelled_as_modelled' tests/unit/test_simulation_view.py
---


**Problem.** The interface carries a use disclaimer but no interpretation one, so nothing tells a reader the compartment readouts and chart traces are modelled rather than measured

**Why it matters.** `docs/MODEL.md` states that no displayed value may be read
as accurate to its last digit as a prediction about a patient, and that sentence
lives only in a specification a learner will never open. The interface's own
standing notice is an *educational-use* disclaimer: it says what the tool is
*for*, not how to read a number on it. Those are different claims, and only the
second addresses this hazard.

The compartments this project exists to display - vessel-rich, muscle, fat,
mixed venous - are precisely the ones no monitor shows, so a reader has no
measured counterpart to check a trace against, and the polish of the display
argues the other way. `docs/MODEL.md` § "Reasonably foreseeable misuse, and the
hazards the presentation carries" carries this as the one row whose mitigation
is incomplete, and names this item as where the rest lives (`PL-FDBK`).

**The project owner has agreed the interface should carry an interpretation
statement distinct from the use disclaimer** (2026-09-13, answering `PL-FDBK`).
The wording and placement are open.

**The pattern to follow already exists in the codebase**, which is the reason
this is small. The control-input timeline labels its marks `"Settings only - not
a measurement."` at `src/anesthesia_sim/app/simulation_view.py`, held by
`test_the_interface_says_a_control_mark_is_an_input_not_a_measurement`. It works
because it is short, sits beside the thing it qualifies rather than in a banner,
and says what the value *is* instead of what the user must not do. `README.md`
carries the global form of the claim - "Every value on screen is a model output,
never a measurement" - which is the sentence to adapt.

**Where.** `src/anesthesia_sim/app/simulation_view.py` (the compartment readouts
and the chart), `tests/unit/test_simulation_view.py`, and `docs/MODEL.md` §
"Minimum displayed outputs" if the statement becomes required rather than
optional.

**Open questions for the owner**, both editorial: the exact wording, and whether
it sits once beside the readout block or is repeated on the chart. Worth noting
that repeating a disclaimer is how it stops being read, so once is the default
unless the chart is separable from the readouts in use.

**Done when.** The interface states, beside the modelled values themselves, that
they are model outputs rather than measurements; a test names the string; and
`docs/MODEL.md`'s hazard row is updated from "partially mitigated" to naming
that test.

**Verified 2026-09-14.** The interface carries exactly one notice, at
`app/simulation_view.py:3113-3122`: "Educational simulation only. This
idealized model is not a clinical prediction, monitoring, or dosing tool." That
is a **use** disclaimer - it says what the tool may not be used for. Nothing
anywhere says what the numbers on screen *are*: that every compartment readout
and every chart trace is a modelled state computed from the run's definition,
not a measurement of anything.

**Why it matters, and why the existing notice does not cover it.**
`CLAUDE.md`'s safety-critical standard states this as its own requirement,
separately from the disclaimer: "Clearly distinguish modeled/internal states
from measured or directly observable quantities. Do not present a predicted
value in a way that could reasonably be mistaken for a measurement." And, in
the same section, "Disclaimers do not lower the engineering standard for these
paths." The readouts are laid out like a monitor and the traces look like
captured data, so the default reading of the screen is the wrong one; a notice
about permitted *use* does not correct a misreading about what the numbers
*are*. The compartment values are the sharpest case - a venous or muscle
partial-pressure-equivalent fraction has no measured counterpart at all, so
there is nothing a reader could have observed that it corresponds to.

**Where the content comes from, and it is mostly already written.**
`docs/MODEL.md` already derives what a displayed value may imply - the
displayed-precision section, the known limitations, and the hover-readout
derivation `PL-YLKR` added - so this is a build against an existing
specification plus the one sentence that specification does not yet carry:
which displayed quantities are modelled states and which, if any, correspond to
something observable.

**The port carries it rather than deferring it.** The Qt port rewrites this
surface, so the placement will move; the content will not, and leaving the gap
open across a whole milestone is the outcome the standard exists to prevent.
Whoever builds the dashboard on PySide6 should take this with them rather than
after them.

**Done when.** A reader of the running interface can tell, without leaving it,
that the compartment readouts and the chart traces are modelled predictions
rather than measurements - and `docs/MODEL.md` states which displayed quantities
are modelled states, so the interface's wording is traceable to the
specification rather than invented in the view. `tests/unit/test_simulation_view.py`
asserts the distinction is present.
