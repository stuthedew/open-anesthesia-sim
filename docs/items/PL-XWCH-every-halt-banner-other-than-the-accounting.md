---
id: PL-XWCH
title: Every halt banner other than the accounting check's shows the exception's class name and its developer message to the learner, because halt_disposition records '{TypeName}: {message}' and the banner prints it whole (found in PL-TWZY)
priority: P2
effort: M
status: ready
classes: ux
feature: interface-design-review
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/qt_widgets.py, docs/INTERFACE.md
added: 2026-11-22
filed-pr: 2259
payoff: a learner whose run stops on a simulator fault reads in plain words what kind of fault it was, and can copy the details into a report
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
