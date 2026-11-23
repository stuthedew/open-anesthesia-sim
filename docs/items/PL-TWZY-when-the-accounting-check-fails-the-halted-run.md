---
id: PL-TWZY
title: When the accounting check fails, the halted-run notice shows core's developer message to the learner, with e-notation and code names such as absolute_error=
priority: P3
effort: S
status: done
classes: ux
feature: interface-design-review
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/main.py, src/anesthesia_sim/app/formatting.py, docs/INTERFACE.md, tests/integration/simulation_view/test_simulation_view_run_stops_itself.py, tests/integration/test_failure_log.py, tests/unit/test_dashboard_frame.py, tests/integration/approved_interface_strings.json
added: 2026-11-22
closed: 2026-11-22
pr: 2259
payoff: a learner whose run halts on a failed accounting check reads why in plain words
tests: tests/integration/simulation_view/test_simulation_view_run_stops_itself.py::test_an_accounting_halt_tells_the_learner_in_words_and_logs_the_totals, tests/integration/test_failure_log.py::test_a_failure_logged_by_a_run_reaches_the_file_in_the_data_directory, tests/integration/test_failure_log.py::test_a_data_directory_that_cannot_be_made_keeps_no_file_and_lets_the_launch_go_on
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

**Decided and built, 2026-11-22.** The halt banner gives the learner plain
words, and the core's message, with its totals, goes to the application's log
for a developer. The core's message is unchanged, because a developer reading a
log or a traceback is its reader. Research taken before the change, each page
read on 2026-11-22:

1. Nielsen Norman Group, "Error-Message Guidelines"
   (https://www.nngroup.com/articles/error-message-guidelines/): "Avoid
   technical jargon and use language familiar to your users instead", and
   "Hide or minimize the use of obscure error codes or abbreviations; show them
   for technical diagnostic purposes only."
2. Microsoft, Win32 "Error Message Guidelines"
   (https://learn.microsoft.com/en-us/windows/win32/debug/error-message-guidelines):
   "If a message has multiple audiences, you may need to provide separate text
   for administrators, end users, and developers", and "If the error is a
   critical error, write it to the event log." It asks a message to say what
   happened and why, and what the user can do.
3. Google, Technical Writing, "Write for the target audience"
   (https://developers.google.com/tech-writing/error-messages/target-audience):
   avoid jargon or technical terms the audience may not understand.
4. OWASP Error Handling Cheat Sheet
   (https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html):
   "the error details are logged server side for investigation, and not
   returned to the user."

All four point the same way, so no option was put to the owner. The banner
says what happened (the check failed and the step was rejected), why it
matters to a learner (a fault in the simulator, not a change in the patient),
and what to do (the banner's existing exit, Reset). The rejected step's
amounts are on the accounting panel beside it, so the banner does not repeat
them. The wording is a placeholder, and it changes what a halt tells a
learner, so its pull request records the owner's read.

`dashboard_frame.shown_failure_reason` chooses the words for every failure
banner. `RunView.halt` logs a run's own failure with its traceback at error
level, and `SimulationView._halt_every_run` logs a dashboard exception once.
`main.open_failure_log` writes the package's error records to `failures.log`
in the reader's data directory, beside the saved Workspaces, as well as to
standard error, so the record survives a launch with no terminal.

**Blind review, 2026-11-22.** Pass 1: F1 should-fix, fixed. The first wording
said the delivered, exhausted and stored amounts "did not add up", but the
check fails at a residual far below the 0.1 L the panel shows, so the panel's
amounts can look balanced. The banner now says what a failed check means: the
rejected step created or lost agent. F2 optional, fixed: the residual
formatter's docstring still said the banner printed the signed amount. F3
optional, rejected: an accounting error raised with no check of the right type
still shows the developer's message, but no code raises one, and `PL-XWCH`
covers every banner that shows a raw message. Pass 2: F1 should-fix, fixed:
the log reached standard error only, so a launch from an icon lost it; the
failure log file was added. F2 optional, fixed: a run halted twice logged
twice, the second time with a cause the run had not recorded; a run now logs
its first failure only, under its name.

**Blind review, second round, 2026-11-22.** Both passes found the same
should-fix, fixed: `open_failure_log` let an `OSError` from making the
directory or opening the file stop the launch, where the Workspace and
preference stores carry on with a notice. It now returns None, and
`test_a_data_directory_that_cannot_be_made_keeps_no_file_and_lets_the_launch_go_on`
failed before the fix with `FileExistsError: [Errno 17] File exists`. Pass 2
also found, as should-fix, and pass 1 as optional, that the first round's
guard was wrong: it dropped the dashboard's own exception when the frame
failed on a run that had already failed, and a dashboard exception was logged
once for each run. Fixed: a run logs only its own failure, and
`SimulationView._halt_every_run` logs a dashboard exception once, as "Every
run on the dashboard stopped on a failure". The accounting test now expects
that second record in the case with no frame drawn.

**Regression test run before the fix.** With `src/` stashed,
`uv run pytest -q "tests/integration/simulation_view/test_simulation_view_run_stops_itself.py::test_an_accounting_halt_tells_the_learner_in_words_and_logs_the_totals"`
failed in both cases with `AssertionError: Simulation stopped —
AgentSimulationValidationError: Agent accounting validation failed, so the
step was rejected and rolled back. The rejected step's totals:
unaccounted=6.000000e+00 L, ...`.

**Generator check.** The route is still open for other failures:
`halt_disposition` records `"{TypeName}: {message}"`, and every other failure
banner shows it. Those failures are defects with no plain cause a learner
could act on, and their banners already say Reset is the way out. Filed as
`PL-XWCH` (the other halt banners) rather than widened here; this chain takes it next.

**Docs swept:** `docs/INTERFACE.md` (§ "Every value and what qualifies it come
from one step", § "Displayed precision"), `docs/MODEL.md` and
`docs/VERIFICATION.md` (grep for the banner and the six-decimal form: no
mention).
