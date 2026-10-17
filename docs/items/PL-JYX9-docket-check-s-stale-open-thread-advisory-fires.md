---
id: PL-JYX9
title: docket check's stale-open-thread advisory fires on every run on docs/WORKING_NOTES.md's desflurane thread, its own documented permanent false fire, so it never changes a decision
priority: P3
effort: S
status: done
classes: defect
feature: friction-batch
milestone: v0.5.25
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_checks.py, subprojects/docket/README.md
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-09-25
closed: 2026-10-17
pr: 1491
payoff: make check stops printing stale-thread lines on every run, and the advisory meets the one session that can act on it
verify: grep -q 'def test_stale_threads_are_named_only_where_the_notes_file_changed' subprojects/docket/tests/test_checks.py
---

**Problem.** docket check's stale-open-thread advisory fires on every run on docs/WORKING_NOTES.md's desflurane thread, its own documented permanent false fire, so it never changes a decision

Observed on every run of `docket check` in the stress test. `CLAUDE.md`: a check that fires every run without changing a decision is a defect in the check.

Reproduced 2026-09-25 against 46954a81: `bin/docket check` names one stale thread, the desflurane one, and nothing else. No open-thread heading has been deleted from `docs/WORKING_NOTES.md` since the advisory landed on 2026-09-21 (PL-DG84), so it has not yet changed a decision; its own docstring records that on landing it named four threads, three of them already filed as items.

**Generator check.** One-off, removed from PL-GPJ7's `root-cause-of` and from the `exact-gates` feature: it is an advisory, not a hard gate, inferring that a thread is spent from its cited items all being closed, and the one thread it names outlived its items for a reason no item records, as its docstring predicted. No head's `misread:` states whether a notes thread is still open.

**Why it matters.** Every session reads past it, and a real stale thread arriving beside it is read past too.

**Done when.** The advisory names a stale thread only in a branch that changes
`docs/WORKING_NOTES.md`, a test in `subprojects/docket/tests/test_checks.py`
pins that a branch leaving the file alone gets no line, and its docstring
records the decision it serves and where that decision is taken (`PL-1XZD`).

**Decision needed.** Retire the advisory, or give a thread a way to be acknowledged. It is a session's call rather than the owner's - an internal check whose reach is one advisory line - but it is the next step, so the item waits on it rather than on work.

- **Retire it**: delete `_check_stale_open_threads` and its eight tests. The cheapest route, and the outcome the project's instructions name for a check that fires every run without changing a decision.
- **A dated acknowledgement** the advisory honours: a new marker every notes-file writer has to learn, built for one thread.
- **Re-head the thread**, which the advisory's own message asks for: a docs-only edit, but the heading would stop saying the thread is open when the docstring says it genuinely is - rewording to satisfy a check.

**Recommendation:** retire it. Its record is one permanent false fire and no decision changed. What would change this is a second thread named by it and acted on, which four days have not produced.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

**Measured again 2026-10-12, in the first batched design round, against
`origin/main` at 919ad967.** `bin/docket check` now names three threads, not
one: the desflurane thread, the v0.2.8 gate's membership test (its three items
closed 2026-08-31 and 2026-09-01) and "item 34's two releases" (its seven
items closed by 2026-09-26). The second and third are what the advisory was
built to find - threads that outlived their items with nothing re-heading or
deleting them - and they have sat named for at least sixteen days. So the
premise above is half refuted and half confirmed: the advisory does find real
stale threads, and nobody acts on them where it fires.

**Decided** (a session's call, as the brief says): neither retire nor
acknowledge; route. `CLAUDE.md`'s advisory rule (project owner, 2026-10-01,
ratified, `PL-1XZD`) retires an advisory only after naming the decision it
was built to change and where that decision is taken, routes it there first if
the decision is still taken, and retires it only if it still changes nothing
there. The decision is whether to re-head or delete a notes thread whose items
have all closed; it is taken when a session writes `docs/WORKING_NOTES.md` -
at a close-out's docs sweep, or at the session end `CLAUDE.md`'s capture rule
names - and it is still taken. So the advisory fires only in a branch that
changes `docs/WORKING_NOTES.md`, read from the changed paths `cmd_check`
already holds (`vcs.changed_paths`), and prints nothing on every other run.
The desflurane thread still appears in such a branch, and its own paragraph
says that fire is correct; it costs one line at the one moment a session is in
the file. Retiring the advisory loses two true positives; a dated
acknowledgement is a new marker built for one thread, which the pause on new
workflow mechanisms would hold in any case. Changing an existing advisory's
firing condition repairs a check that fires every run without changing a
decision, which `CLAUDE.md` calls a defect in the check, so the pause does not
hold it. The number that retires it after routing: a branch that changed the
notes file with the advisory in its output and both stale threads still
standing afterwards.

The two threads it names are repaired under `.claude/rules/citation-drift.md`'s
licence by whichever session next edits `docs/WORKING_NOTES.md`, declaring the
file in its item's `touches`; no item is filed for them, since the advisory is
their record and will fire where the repair is made.
