---
id: PL-DST3
title: push-check-guard.sh kills a check that passes its 100 s deadline and lets the push go with only the skill note, and doc_check alone now takes 77-101 s, so a push can go out with checks unrun and nothing saying so
priority: P2
effort: S
status: done
classes: defect
feature: guards-say-when-they-cannot-check
touches: .claude/hooks/push-check-guard.sh, tests/unit/test_push_check_guard.py
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
closed: 2026-11-03
pr: 1990
payoff: a push whose checks never finished says so, so a session does not report it as checked
verify: grep -q 'def test_a_check_killed_at_the_deadline_is_named' tests/unit/test_push_check_guard.py
---

**Problem.** push-check-guard.sh kills a check that passes its 100 s deadline and lets the push go with only the skill note, and doc_check alone now takes 77-101 s, so a push can go out with checks unrun and nothing saying so

**Why it matters.** The push guard runs the checks CI would fail on before a
push leaves the machine. When the checks run past its 100-second deadline the
guard kills them and lets the push go with only the skill note, so the session
cannot tell a push whose checks passed from one whose checks never finished.
`tools/doc_check.py check` alone took 38 s in this thread's container on
2026-11-03, and the review measured 77 to 101 s, so how often the deadline is
passed depends on the machine, and nothing says when it was.

**Done when.** A push whose checks were killed at the deadline goes out with a
note saying which checks did not finish, and a test with a check that sleeps
past a shortened deadline finds that note.

**Generator check.** A member of `PL-9KSJ`: the guard let a push through
unchecked and said nothing.

**Fixed 2026-11-03 (#1990).** The guard now lists each check that gave no
answer: one stopped at the deadline, and one that crashed or exited with a
status other than 0 or 1. The push still goes, and the note says the push was
not checked against those checks. A refused push names them too. Tests cover a
check that sleeps past a two-second deadline, set through
`PUSH_CHECK_GUARD_DEADLINE`, and a check that raises.
