---
id: PL-FN11
title: An item that changes code records, when it closes, the pytest node ids of the tests that show its work, and docket checks once that each test is defined and that the closing branch added or changed it, in place of a verify: command
priority: P2
effort: M
status: untriaged
classes: infra
feature: standing-weight
touches: subprojects/docket/src/docket, subprojects/docket/tests, subprojects/docket/README.md, .claude/skills/docket/modes/triage.md, .claude/skills/docket/modes/close-out.md, .claude/skills/docket/modes/start.md, docs/worker.md
added: 2026-11-21
payoff: a code item's proof is the tests it added, named when they exist, so no session guesses a test name at triage
---

**Problem.** An item that changes code records, when it closes, the pytest node ids of the tests that show its work, and docket checks once that each test is defined and that the closing branch added or changed it, in place of a verify: command

**Why it matters.** The project owner chose this form on 2026-11-21 (`PL-LFJZ`, the count of what a test-named done-condition would have prevented). Of the 35 items under the root causes about `verify:` commands, it would have prevented 11 when the test is named at close, against 9 when it is guessed at triage: `PL-0M32` and `PL-6TN8` were both a test name guessed before the work. Checking once at close matters too: of 1,060 closed items whose condition named a test, 109 now name one that was later renamed or removed. At triage the item still says in words, under **Done when.**, what will be true. Code that only deletes something is `PL-N046`'s, since a deletion has no new test to name.

**What to do.** Give an item a `tests:` field that holds pytest node ids, such as `subprojects/docket/tests/test_done.py::test_names_a_test_the_branch_added`, separated by commas. `bin/docket set ID --status done --tests '...'` writes it when the item closes.

1. An item at `ready` no longer needs a `verify:` command. Its **Done when.** section says in words what will be true, and `bin/docket check` already requires that section. An item is no longer withheld from a delegated worker for having no command.
2. A closed item is no longer asked for a `verify:` command where it records `tests:`.
3. `bin/docket check` reads the closures that the checkout introduces, which are the items `done` here and not `done` on the default branch. For each node id it checks that the file defines the test, and that the test is new or differs from its copy at the commit where the branch left the default branch. An item already closed on the default branch is never read again.
4. `bin/docket verify` reports the same check in place of running a command, and it no longer stops at an open item that records no command.
5. `.claude/skills/docket/modes/triage.md`, `.claude/skills/docket/modes/close-out.md`, `subprojects/docket/README.md` and `docs/worker.md` describe the new form.

**Done when.** An item that changes code can go from `ready` to `done` carrying `tests:` and no `verify:`, and `bin/docket check` on its branch fails when a named test is not defined or the branch did not add or change it.

**Generator check.** None: work the project owner chose in `PL-LFJZ` (the count of what a test-named done-condition would have prevented).
