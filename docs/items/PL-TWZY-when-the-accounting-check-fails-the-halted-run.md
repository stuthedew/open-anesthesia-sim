---
id: PL-TWZY
title: When the accounting check fails, the halted-run notice shows core's developer message to the learner, with e-notation and code names such as absolute_error=
priority: P3
effort: S
status: ready
classes: ux
feature: interface-design-review
touches: src/anesthesia_sim/core/agent_simulation_validation.py
added: 2026-11-22
payoff: a learner whose run halts on a failed accounting check reads why in plain words
---

**Problem.** When the accounting check fails, the halted-run notice shows core's developer message to the learner, with e-notation and code names such as absolute_error=

**Found** while working `PL-8V6L` (the accounting panel's residual lines), on
2026-11-22. That item rewrote the residual lines' power of ten in superscript
digits. It left this message alone, because the message is raised in `core/`,
and a defect in `core/` is filed rather than fixed in passing.

**What a learner would see.** When the accounting check fails, the step is
rolled back and the run halts. `AgentSimulationValidationError`'s message in
`src/anesthesia_sim/core/agent_simulation_validation.py` reads, in part,
"The rejected step's totals: unaccounted=1.000000e+00 L,
absolute_error=1.000000e+00 L, relative_error=...". `docs/INTERFACE.md`
§ "Displayed precision" says the failure notice prints the signed unaccounted
amount with six decimal places. Whether the halt banner shows the message
whole is to be checked in `app/run_view.py`'s `_halt_run`.

**Why it matters.** `.claude/rules/plain-writing.md` names e-notation among
what a clinician reader is not expected to know, and `absolute_error=` is a
code name. The message has two readers: the learner who sees the halt, and a
developer reading a log. The signed values at six decimals are for the second.

**What to do.** Decide what the halt banner shows the learner, in words, and
keep the full developer form for the log and the traceback. Not decided here.

**Done when.** A test halts a run on a failed accounting check and finds no
e-notation and no code name in the text the halt banner shows.

**Generator check.** Possibly one route with several instances: `_halt_run`
shows `str(error)` from `core/` verbatim, so every `core/` error message is
learner text (`tools/glyph_check.py` names the same route). Not counted here.
