---
id: PL-LKGK
title: Give a halted run's banner a Copy details block a learner can paste into a bug report: platform, scenario and settings at the halt, step size, the failed check, recent actions and a loadable state
priority: P3
effort: M
status: dropped
classes: feature, ux
added: 2026-10-19
closed: 2026-10-20
reason: deferred at the project owner's word on 2026-10-20: build only if halted runs cause trouble before scenario save and load exist
---

**Problem.** Give a halted run's banner a Copy details block a learner can paste into a bug report: platform, scenario and settings at the halt, step size, the failed check, recent actions and a loadable state

**What the halted-run notice has today** (checked on `main` at `5c6b20ab`, 2026-10-19):

- A failure halts the run with the reason `dashboard_frame.halt_disposition` records, the exception's type and message. The banner shows it through `FAILURE_NOTICE_TEMPLATE` or `UNDRAWN_FAILURE_NOTICE_TEMPLATE` in `src/anesthesia_sim/app/dashboard_frame.py`, followed by "Reset to start a new run." Pull request #1676 (open on 2026-10-19) makes the core's refusals name the compartment, the value that failed and the capacity it was checked against. Once it merges, the banner says which check failed and by how much.
- The banner is `NoticeLabel` in `src/anesthesia_sim/app/qt_widgets.py`, a plain `QLabel` with no text-selection flag. A learner cannot select or copy even that one line.
- No copy, export, save or report action exists anywhere in the interface. No traceback is kept: nothing under `src/anesthesia_sim/` logs, installs an exception hook or records a stack.
- Some of what a report needs is already held. The build version and commit are `APP_BUILD_VERSION` in `src/anesthesia_sim/app_metadata.py`, and the subtitle already shows them. `SimulationController.record()` returns a `RunRecord` with the agent, the four settings in force, the simulated time and the failure reason. `RunRecord.control_timeline` holds every setting change the model saw, with its time, as `ControlChange` records from `src/anesthesia_sim/app/control_record.py`.
- What is missing: the operating system, Python and Qt versions; the step size; the traceback; and any loadable saved state. Scenario save and load are items 9 and 10 of `ROADMAP.md` § "Planned milestones", and neither is built.

**Why it matters.** A learner who hits a halt can report only what they can retype, and the banner's one line is not enough to reproduce the bug. Common guidance splits an error into two layers: one plain line for the user, and details a developer can use ([NN/g error-message guidelines](https://www.nngroup.com/articles/error-message-guidelines/); [Microsoft error-message guidance](https://learn.microsoft.com/en-us/windows/win32/uxguide/mess-error)). Here that means a learner line and a "Copy details" block. The learner line says the simulation hit an internal error and stopped, that it is a bug and not something the learner did, and what to do next. The block is text the learner can paste into an email or an issue. The banner's present wording, a Python exception name followed by a field name, is written for a developer, and it is the only layer there is.

**Proposed shape**, for the decision rather than settled:

- A "Copy details" button beside the failure banner. It is offered for a failure only, not for the supported run length, which is not a bug.
- The copied text is plain and labelled, with units on every value. It holds the app version and commit; the operating system, Python and Qt versions; the agent, the patient and the four settings at the halt (vaporizer dial, fresh gas flow, ventilation, cardiac output); the simulated time and the step size; the failed check's type, message and traceback; and the learner's last setting changes with their times.
- The model is deterministic, so the version, the starting settings and the whole `control_timeline` may reproduce the run without a state file. Putting the whole timeline in the copied text could stand in for a loadable state until scenario save and load exist.

[superseded 2026-10-20: answered below, at the project owner's word during the v0.6.0 test drive] **Decide at the v0.6.0 test drive** (project owner, 2026-10-19, ratified, over deciding it now and over holding #1676 for it). Three questions: whether to build this in v0.6.0 or later; whether the banner gets a separate plain learner line or keeps its present wording; and whether the loadable state waits for scenario save and load or ships as the control timeline in the copied text. This item is not in the Order and not in v0.6.0's required scope unless the project owner adds it then.

**Done when.** A halted run's failure banner offers Copy details. The copied text carries every field the decision keeps, each labelled with its units and stated as the run's state at the halt. A test forces a failure and pins the copied text.

**Answered 2026-10-20, during the v0.6.0 test drive.** The project owner answered all three questions in the project chat, each against the coordinator's post that put it.

1. **Build it in v0.6.0 or later: later, and only if halts cause trouble first** (project owner, 2026-10-20, ratified on the coordinator's recommendation of later, over building it in v0.6.0; the condition for building it is his own). At 01:22:59Z he wrote: "Let's defer and not implement unless we are having issues when we need it and haven't implemented save and load yet". The coordinator then asked whether to ship only the plain learner line in v0.6.0, and at 01:23:53Z he wrote: "yeah, defer that". So nothing from this item goes into v0.6.0, the learner line included. The item is not on the Order and not in v0.6.0's required scope.
2. **A separate plain learner line: yes, when the item is built** (project owner, 2026-10-20, ratified, over keeping the banner's present developer-only wording). At 01:22:12Z he wrote: "Yes to separate line for learners." The coordinator's example of the line was "The simulation hit an internal error and stopped. This is a bug, not something you did." The technical line stays beneath it for the developer.
3. **The timed change list is a debugging aid only, until save and load exist** (project owner, 2026-10-20). At 01:22:12Z he asked: "The timed change list is just for debugging until save and load is implemented?" The coordinator confirmed at 01:22:23Z that learners would not use it as a save, and that once save and load exist the block would attach a saved state instead. That the list rebuilds the run is inferred from the model being deterministic. Nobody has yet replayed a real halt to test it.

**Dropped on 2026-10-20 as deferred, with the condition for reopening it.** The answer leaves no work any session should start now, and an open item would be offered by `bin/docket next`. Reopen it, and build it with the learner line from answer 2, when halted runs are causing trouble while scenario save and load (items 9 and 10 of `ROADMAP.md` § "Planned milestones") are still unbuilt. If save and load exist by then, the block attaches a saved state in place of the timed change list, as answer 3 says.
