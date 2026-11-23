---
id: PL-HPD0
title: A dial whose thumb is still held when its run starts over (an agent change or a Reset) applies its release value to the new run, though the preview of that value ended at the start-over (found building PL-1WFW)
priority: P2
effort: S
status: needs-decision
classes: defect
feature: interface-design-review
touches: src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/run_view.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no learner sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-22
payoff: a learner who holds a dial through a reset does not set the new run without meaning to
---

**Problem.** A dial whose thumb is still held when its run starts over (an agent change or a Reset) applies its release value to the new run, though the preview of that value ended at the start-over (found building PL-1WFW)

**Found 2026-11-22** by the worker building `PL-1WFW`. That item ends a held preview when its run starts over or is renamed, so no label names an agent or run that is gone. The thumb is still down, though, and its release applies the value to the new run as an ordinary change. Whether a release after a start-over should apply is open: a learner who held the dial through a key press that reset the run may not mean to set the new run. The behaviour is unchanged from before `PL-1WFW`.

**Why it matters.** A learner who held a dial while a key press reset the run can set the new run without meaning to. The value is shown, so nothing is hidden, but the change was not the learner's choice for that run.

**Decision needed.** When a run starts over while a dial's thumb is held, should the release apply the value to the new run, or should the gesture end at the start-over and the release do nothing?

**Recommendation (provisional).** End the gesture at the start-over, so the release applies nothing, because the preview it belonged to has already ended and the learner never saw the value previewed on the new run. Research on how platforms treat a drag whose target is replaced is owed before this reaches the owner.

**Done when.** The decision is recorded here, and a test holds a dial across an agent change and a Reset and shows what the release does.

**Generator check.** A one-off, found building `PL-1WFW`; the behaviour predates it.
