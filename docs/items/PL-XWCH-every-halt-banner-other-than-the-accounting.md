---
id: PL-XWCH
title: Every halt banner other than the accounting check's shows the exception's class name and its developer message to the learner, because halt_disposition records '{TypeName}: {message}' and the banner prints it whole (found in PL-TWZY)
priority: P2
effort: M
status: done
classes: ux
feature: interface-design-review
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/qt_widgets.py, docs/INTERFACE.md
added: 2026-11-22
closed: 2026-11-23
pr: 2269
filed-pr: 2259
payoff: a learner whose run stops on a simulator fault reads in plain words what kind of fault it was, and can copy the details into a report
tests: tests/unit/test_failure_words.py::test_each_kind_of_failure_has_its_own_plain_words_and_no_developer_message, tests/integration/simulation_view/test_simulation_view_failure_details.py::test_a_failed_step_is_worded_for_the_learner_and_its_message_kept_in_the_details, tests/integration/simulation_view/test_simulation_view_failure_details.py::test_a_halt_of_each_kind_is_worded_by_its_kind_and_named_in_the_details, tests/integration/simulation_view/test_simulation_view_failure_details.py::test_show_details_reveals_the_details_copy_and_the_report_line
---

**Problem.** Every halt banner other than the accounting check's shows the exception's class name and its developer message to the learner, because halt_disposition records '{TypeName}: {message}' and the banner prints it whole (found in PL-TWZY)

**What a learner sees.** `halt_disposition` in `app/dashboard_frame.py`
records a failure as `"{TypeName}: {message}"`, and every failure banner prints
that reason whole: "Simulation stopped — RuntimeError: ...". The run's branch
and resume refusals quote it too. Only the accounting check's failure is
worded for the learner, since `PL-TWZY`.

**Why it matters.** A learner whose run stops on a simulator fault meets an
exception's class name and a message written for a developer, at a moment
that already alarms, and is not told whether the patient changed. The
developer still needs the exception and its traceback, which the failure log
has held since `PL-TWZY`.

**Done when.** No failure banner shows an exception's class name or its
message. Each kind of failure the simulator can tell apart has its own plain
words, and a test halts a run on each kind and reads them in the banner. The
exception, with its message and traceback, still reaches the failure log.

**Generator check.** One route, found while fixing `PL-TWZY`: every failure
banner printed the recorded reason, which `halt_disposition` builds from the
exception's class and message for a developer. That route is this item, and
no other item has come from it. `tools/glyph_check.py` names the same route
for the characters it checks.

**Research, read 2026-11-23.** Microsoft's Windows design guidance on error
messages (https://learn.microsoft.com/en-us/windows/win32/uxguide/mess-error),
read in full from the page:

1. "Use a different error message (typically a different supplemental
   instruction) for each detectable cause", and "Use a message with multiple
   causes only when the specific cause can't be determined."
2. Under "Handling unknown errors": "If you can't suppress an unknown error,
   it is better to be up front about the lack of information." And "Don't
   provide a problem, cause, or solution unless it is likely to be right."
3. It names, as a poor message, one that "indicates that there is a bug in the
   program. This error message has meaning only to the programmer", and lists
   log files as the place for information meant for IT professionals.

`PL-TWZY`'s brief quotes the Nielsen Norman Group, Google and OWASP guidance,
which says the same about technical detail: keep it out of the user's
message and in a log.

**Decided, 2026-11-23.** Every failure banner, and not the run-length stop,
gets a "Show details" control. It reveals the application's version, the
exception's type and message, and where the failure log is, with a "Copy
details" button and one line linking to the project's issue page that says to
attach the copied details. The banner's own sentence stays in plain words.
Microsoft's guidance (above) puts advanced detail and error codes behind a
Show/Hide details control, and the Nielsen Norman Group shows error codes
"for technical diagnostic purposes only". Microsoft also says not to send the
user to support for a problem they can solve themselves; a simulator fault is
one they cannot, so a report route is the useful next step (project owner,
2026-11-23, ratified, "Agree with best practice", over keeping reporting out of
the application). The detail panel also keeps reachable the specifics that
some messages give today, such as which compartment held a non-finite value
(`PL-TCNT`). The wording comes back to the owner with screenshots.

**First build attempt, 2026-11-23.** Mapping each exception type to plain
words in `halt_disposition` fails 45 tests that read the exception's type or
message in the recorded reason, among them `PL-TCNT`'s requirement that the
notice names the compartment. So the recorded reason keeps the developer form
for the details panel and the log, and the run records the failure's kind
beside it when it halts, from which the banner takes its plain words. The
kind is recorded, not read back from the reason's text.

**Built, 2026-11-23.** `app/failures.py` sorts an exception into a
`FailureKind`, most specific type first, and `SimulationController.fail`
records the kind beside the reason. `RunStatus` refuses one without the
other, so `tests/unit/test_supported_range_edges.py` now builds the run's
settings, record and snapshot through `RECEIVERS`. The banner reads its
words from `dashboard_frame.FAILURE_CAUSE_TEXTS` and adds that the fault is
the simulator's and not the patient's. `qt_widgets.FailureDetails` sits
under the banner, in one container with it that is hidden while both are.
The issue page's address is written once, in `pyproject.toml`'s
`[project.urls]`, and `app_metadata.project_url` reads it from the installed
metadata. The link takes its colour from inline style, because a palette
written wholesale on the label carries the platform's disabled colours with
it, which `tools/contrast_check.py` refuses.

**Regression run on the code before the fix.** A variant that needs no new
interface was run on `origin/main` (64d3533a) in a scratch worktree: a real
failed step through `_StepFailingController(_real_step_failure())`, then
`assert "SimulationNumericalError" not in banner`. It failed with
`AssertionError: Simulation stopped — SimulationNumericalError: the simulation
step of 1 s could not be completed and was rolled back, ...`. The same
assertion is in
`test_a_failed_step_is_worded_for_the_learner_and_its_message_kept_in_the_details`.

**Blind review, two passes.** Both found that a Reset refused after an
earlier failure was named nowhere on screen (fixed: a "Reset was then
refused" line in the details), that the copied details did not say which of
two runs stopped (fixed: a "Stopped run" line while two runs are drawn), and
that the log's path carried the login name into a public issue (fixed: the
path is written from `~`). Pass 1 found the link could not be reached from
the keyboard (fixed: keyboard link flags and tab focus), that configuration
and execution failures were never halted through the run view in a test
(fixed), that two integration tests compared the widget with itself (fixed:
the expected details are built from the error), and two stale comments
(fixed). Pass 2 found the configuration words could be read as the learner's
own dial (fixed: "one part of the simulator gave another a value that it
does not accept"). Pass 2 also found that two runs' "Show details" buttons
read alike to a screen reader (fixed: each button's accessible name adds the
run's name while two runs are drawn). Not fixed here: on X11 with no
clipboard manager, copied details are lost when the application closes,
which the refused-Reset banner asks the learner to do. The failure log keeps
the message. `PL-PYWF` records the clipboard gap.

**Docs checked, 2026-11-23.** `docs/INTERFACE.md` (the failure banner, Show
details and the refused-Reset paragraph, rewritten in this branch),
`docs/ARCHITECTURE.md` (the package map, which now lists `app/failures.py`,
and § on halts, where the snapshot now carries the failure's kind beside its
reason), `README.md`, `docs/MODEL.md` and `docs/VERIFICATION.md` (no
statement about the banner's words). The other places that name
`pyproject.toml`, `controller.py` or `dashboard_frame.py` describe other
parts of those files and stay true.
