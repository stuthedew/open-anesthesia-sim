---
id: PL-JYX9
title: docket check's stale-open-thread advisory fires on every run on docs/WORKING_NOTES.md's desflurane thread, its own documented permanent false fire, so it never changes a decision
priority: P3
effort: S
status: needs-decision
classes: defect
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-09-25
---

**Problem.** docket check's stale-open-thread advisory fires on every run on docs/WORKING_NOTES.md's desflurane thread, its own documented permanent false fire, so it never changes a decision

Observed on every run of `docket check` in the stress test. `CLAUDE.md`: a check that fires every run without changing a decision is a defect in the check.

Reproduced 2026-09-25 against 46954a81: `bin/docket check` names one stale thread, the desflurane one, and nothing else. No open-thread heading has been deleted from `docs/WORKING_NOTES.md` since the advisory landed on 2026-09-21 (PL-DG84), so it has not yet changed a decision; its own docstring records that on landing it named four threads, three of them already filed as items.

**Generator check.** One-off, removed from PL-GPJ7's `root-cause-of` and from the `exact-gates` feature: it is an advisory, not a hard gate, inferring that a thread is spent from its cited items all being closed, and the one thread it names outlived its items for a reason no item records, as its docstring predicted. No head's `misread:` states whether a notes thread is still open.

**Why it matters.** Every session reads past it, and a real stale thread arriving beside it is read past too.

**Done when.** Either retired, or a thread can be acknowledged with a dated marker the advisory honours; decide which in the item.

**Decision needed.** Retire the advisory, or give a thread a way to be acknowledged. It is a session's call rather than the owner's - an internal check whose reach is one advisory line - but it is the next step, so the item waits on it rather than on work.

- **Retire it**: delete `_check_stale_open_threads` and its eight tests. The cheapest route, and the outcome the project's instructions name for a check that fires every run without changing a decision.
- **A dated acknowledgement** the advisory honours: a new marker every notes-file writer has to learn, built for one thread.
- **Re-head the thread**, which the advisory's own message asks for: a docs-only edit, but the heading would stop saying the thread is open when the docstring says it genuinely is - rewording to satisfy a check.

**Recommendation:** retire it. Its record is one permanent false fire and no decision changed. What would change this is a second thread named by it and acted on, which four days have not produced.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
