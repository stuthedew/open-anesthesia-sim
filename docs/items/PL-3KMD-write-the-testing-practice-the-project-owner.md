---
id: PL-3KMD
title: Write the testing practice the project owner ratified on 2026-10-17 into a path-scoped rule on the simulator's tests, so a session writing a test takes its expected value from outside the code under test, and close PL-6JKB with it
priority: P2
effort: S
status: ready
classes: docs
feature: tests-detect-wrong-values
touches: .claude/rules/test-oracles.md, docs/items/PL-Y1PS-test-effectiveness-has-been-measured-once-by-a.md, docs/items/PL-6JKB-nothing-checks-that-a-bug-fix-s-regression-test.md, docs/items/PL-75D9-bit-for-bit-determinism-is-tested-only-within.md
added: 2026-10-17
payoff: a session writing a simulator test takes its expected value from outside the code under test, so the next gap like an agent switch that keeps the old agent's compartments is caught when the test is written
verify: grep -q 'fresh run' .claude/rules/test-oracles.md && grep -q '/tests/reference/' .claude/rules/test-oracles.md && ! grep -q 'pauses building new workflow mechanisms' docs/items/PL-Y1PS-test-effectiveness-has-been-measured-once-by-a.md
---

**Problem.** Write the testing practice the project owner ratified on 2026-10-17 into a path-scoped rule on the simulator's tests, so a session writing a test takes its expected value from outside the code under test, and close PL-6JKB with it

**Why it matters.** The 2026-10-17 test-effectiveness audit found four
safety gaps that the whole suite passed over (`PL-QJXS`, `PL-JPS2`,
`PL-ZH1F`, `PL-H1JH`). In each, no test compared the value with an expected
value found independently of the code under test, or the test case was too
small to tell correct code from wrong code. The items fix those four. Only a
rule that loads when a session writes the next test stops a fifth.

**Decision.** The audit's reply recommended a testing practice: take each
expected value from outside the code under test, check a control that changes
a run's state against a fresh run, check stored values against their source,
say what a published-data comparison can detect, and test a rule about a
collection with at least three entries. It also recommended recording each
bug fix's fail-before run (`PL-6JKB`). The project owner agreed with all of it
in that session (project owner, 2026-10-17, ratified, over leaving the
practice as advice in one reply). `CLAUDE.md` says a behaviour change takes
effect in the session that asks for it, so this item writes the rule there.

The rule loads on `tests/unit/`, `tests/integration/` and `tests/reference/`,
which is where a session is reading when it writes a simulator test. It is a
path-scoped rule rather than a check, because whether an expected value is
independent of the code is a judgment no script can make.

The capture of `PL-Y1PS`, `PL-6JKB` and `PL-75D9` said their mechanisms fell
under `CLAUDE.md`'s pause on new workflow mechanisms. That was wrong. The
pause applies only while a workflow-lane head carries `generator: live`. On
2026-10-17 the only head that `bin/docket generators` marked still generating
was `PL-X7D5`, which is a product-lane head. This item corrects the three
briefs and records the decision in each.

**Done when.** `.claude/rules/test-oracles.md` states the practice and loads
on the simulator's test directories; `PL-6JKB` is closed by it; and the briefs
of `PL-Y1PS` and `PL-75D9` record the decision without the wrong claim about
the pause.

**Generator check.** Not a member of any head. It records a decision and
corrects one wrong claim made in a single capture. The claim misread where
`CLAUDE.md`'s generator pause applies, but no other item carries that misreading.
