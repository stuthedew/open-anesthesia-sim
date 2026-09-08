---
id: PL-55DH
title: Build the PySide6 + pyqtgraph spike: the concentration chart and the readout row behind the existing controller, disposable and touching no shipped app/ module
priority: P2
effort: M
status: ready
classes: perf, ux
feature: teachable-case
blocked-by: PL-QXSB
touches: docs/WORKING_NOTES.md
verify: python3 tools/doc_check.py check && grep -q 'PL-55DH' docs/WORKING_NOTES.md
added: 2026-09-08
---

**Problem.** Build the PySide6 + pyqtgraph spike: the concentration chart and the readout row behind the existing controller, disposable and touching no shipped app/ module

**Approved by the project owner, 2026-09-08.** `PL-QXSB` measured PySide6 with
pyqtgraph at 0.51 ms for the frame Flet does in 20.3 ms, flat in point count,
and established that PyQt is excluded by licensing. What it could not measure is
paint cost, because this container has no GPU. The spike is what answers that,
and it is a spike rather than a port: **it throws away cleanly and it changes
nothing shipped.**

**Scope.** The concentration chart and the readout row, driven by the *existing*
`SimulationController` — which needs no adaptation, because `core/` and
`app/controller.py` import no Flet and `tools/import_boundary_check.py` enforces
it. Six traces, the shipped column budget, the same 5 Hz cadence, the four
parameter sliders wired through the same setters.

**Out of scope, deliberately:** the agent selector, the wash-in plot, control
marks, the new-case dialog, the notice banner, theming beyond enough colour to
tell the traces apart. The question is frame cost and feel, not completeness.

**Why it matters.** `PL-QXSB` cannot be decided on this container's evidence
alone, and it is admitted to v0.5.0's gate — so a milestone waits on a question
whose remaining half is one bounded experiment. The spike is also the cheapest
way to be *wrong* about Qt: if the paint cost or the look does not hold up, that
is discovered for a few hours of work rather than after `app/` has been
rewritten. `CLAUDE.md` warns that the apparatus is at permanent risk of becoming
the work; a throwaway spike is the form of this investigation that cannot become
it.

**Where it lives.** Not in `src/anesthesia_sim/app/`. A spike that imports from
the shipped package but is not part of it — so deleting it is one `rm` and no
shipped module ever imported it. Its dependencies are not added to
`pyproject.toml`'s runtime set; `PL-QXSB` records the sizes (PySide6-Essentials
233 MB, numpy 33 MB, pyqtgraph 7.7 MB) that a real port would have to justify.

**Done when** the spike runs a real case end to end and `PL-X9T3` has something
to measure on the owner's machine. Not when it looks finished — that is
`PL-QXSB`'s decision to take afterwards, on evidence.
