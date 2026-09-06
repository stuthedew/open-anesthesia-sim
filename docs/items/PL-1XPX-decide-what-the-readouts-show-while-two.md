---
id: PL-1XPX
title: Decide what the readouts show while two branches are displayed
priority: P1
effort: M
status: needs-decision
classes: safety, ux
feature: scenario-branching
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/formatting.py, docs/MODEL.md
added: 2026-09-06
---

**Problem.** The readouts name a compartment and show one number each. With two
branches displayed, a number that does not say which run it describes is
ambiguous, and there is more than one defensible way to resolve that.

**Why it matters.** `CLAUDE.md` treats presentation as part of safety: the
correct number with the wrong patient context is still a safety failure, and
"which of the two managements is this" is exactly that context. This is also a
mode-awareness problem - a reader who has forgotten which run is selected reads
a correct number as the other run's.

**Decision needed.** What the readouts show while two branches are displayed.
Three candidates, and they are not equivalent:

- **Both runs, paired per compartment.** No mode, no ambiguity, and the
  difference is readable directly. Doubles the readout block, which already
  wraps at some window widths (`PL-3355`).
- **The selected run only, with the selection stated in the readout block.**
  Keeps the current layout. Introduces a mode, which is the thing
  `.claude/rules/expert-review.md` asks to minimize, and a stale selection is
  invisible.
- **Both runs and their difference.** The most informative and the most
  crowded; a difference readout also needs a stated sign convention or it is
  its own ambiguity.

Whichever is chosen, no readout may show a number without naming its run, and
the answer binds the clinical reference band and the control marks too - both
are per-run.

**Where.** `simulation_view.py`'s readout block, `formatting.py` for whatever
label form the answer needs, `docs/MODEL.md`'s minimum displayed outputs.

**Done when.** The question above is answered and recorded here, and the
displayed-outputs section of `docs/MODEL.md` states what a readout names while
two runs are shown.
