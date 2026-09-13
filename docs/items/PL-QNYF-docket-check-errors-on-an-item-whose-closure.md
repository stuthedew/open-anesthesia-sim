---
id: PL-QNYF
title: docket check errors on an item whose closure landed in a queue-only commit, and the error names no remedy the session can reach
status: ready
priority: P2
effort: S
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_a_declined_recovery_names_the_explicit_record_form' subprojects/docket/tests/test_checks.py
added: 2026-09-13
---

**Problem.** docket check errors on an item whose closure landed in a queue-only commit, and the error names no remedy the session can reach

**Found while closing `PL-YDL6`, 2026-09-13**, which made `_number_closing`
decline a pull request number where the closure landed without its work.

**Where.** `checks._check_closures`. The branch that errors fires when
`closures.numbers` has no entry for the item *and* `closures.shallow is False`:

```text
<item>: marked done on `origin/main` but records no `pr`; without it there is
no way back from the closure to the work that made it
```

Before `PL-YDL6` an absent entry meant no commit named a number at all, which is
provenance genuinely lost and worth an error. It now also means *a number was
found and deliberately declined*, because the commit that wrote `status: done`
carried no work. Those are different situations and the second is not a defect in
the item.

**Why it matters.** The error is unsatisfiable from where the session stands.
`bin/docket record` writes nothing, because the recovery is exactly what
declined; `.claude/skills/docket/SKILL.md` forbids editing `pr` by hand and
`record` refuses to overwrite a different number. So `make check` fails with no
action available - the shape `CLAUDE.md` calls out as worse than a missing check,
since it trains a session to route around the output.

There *is* a remedy and the message does not name it:
`bin/docket record <number> --merge <merge commit>`, the explicit form for a
number the base cannot name on its own. A session that has not read that part of
the skill has no way to discover it from the error.

**Bounded.** No item in the store is in this state today - all three known cases
(`PL-3CBS`, `PL-64LS`, `PL-D2GW`) already record the right number by hand, and
`make check` is green. It bites the next item closed in a commit that writes only
to the queue, which the same-commit closure rule (`PL-D2GW`, then `PL-P5S0`) makes
uncommon rather than impossible.

**Approach.** Carry the reason the recovery declined, rather than collapsing it to
an absent number: `ClosureReport` already separates `derived` from `shallow` for
exactly this kind of distinction. Then the error for "the closure carried no work"
names the explicit `record` form, and the error for "no commit names a number"
stays as it is.

**Done when.** An item whose closure landed in a queue-only commit is told that
the recovery declined and why, with `bin/docket record <number> --merge <merge
commit>` named as the way to supply the number - rather than being told its
provenance is lost. The error for a closure no commit names a number for is
unchanged, and `subprojects/docket/tests/test_checks.py` carries a test for each of
the two.
