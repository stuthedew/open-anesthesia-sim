---
id: PL-SHTR
title: docket verify does not set LANDED_GUARD, so an item whose verify: runs docket check --verify replays the whole store one level down
priority: P3
effort: S
status: done
classes: infra
feature: dev-tooling
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-07
closed: 2026-09-25
pr: 1033
verify: grep -q 'def test_a_nested_docket_check_from_verify_declines' subprojects/docket/tests/test_verify.py && uv run pytest subprojects/docket/tests/test_verify.py
recurrences: 2026-09-20 PL-S8JT withdrawn 2026-09-21 PL-34BG, 2026-09-20 PL-34BG withdrawn 2026-09-21 PL-34BG
---

**Problem.** docket verify does not set LANDED_GUARD, so an item whose verify: runs docket check --verify replays the whole store one level down

**Why it matters.** `already_passing` sets both `LANDED_GUARD` and (since
`PL-20CQ`) `VERIFY_GUARD` on the commands it runs, so a nested run asks
neither question twice. `verify_item` sets only `VERIFY_GUARD`. An item whose
command runs `bin/docket check --verify` would therefore make `docket verify`
replay every open item's command one level down - 111 commands and 87 s
measured on the quality job - to answer a question about the store that has
nothing to do with the branch being verified.

Cost rather than correctness: the recursion is bounded, because those children
do carry both guards. No open item records such a command today, so this is a
trap rather than a live defect.

**Done when.** `verify_item` runs the item's command with `LANDED_GUARD` set,
and a test pins that a nested `docket check --verify` declines rather than
sweeping the store.

**Worked.** Both commands `verify_item` runs now take one environment,
`_command_env()`, which sets `LANDED_GUARD` beside `VERIFY_GUARD`: the item's
own command, and the commissioned one `commissioned_result` runs beside a
corrected `verify:`, which the brief did not name but which is the same kind of
child and would otherwise keep the trap for a rewritten command. The test runs
a real nested `docket check --verify` rather than probing the variable, since
the sibling probe for `VERIFY_GUARD` shows only that the variable is set: it
invokes `"$sys.executable" -m docket` with `PYTHONPATH` pointed at the package
source, adds a fixture item `PL-C3C3` whose `verify:` is `touch swept` so a
sweep leaves a file, and runs the same command once outside `docket verify` as
the control that it does sweep. The command ends in `; true` because the
fixture store's items carry only the fields the audit reads, so the nested
check exits 1 on them; the file, not the exit, is the answer. With the fix
reverted the test fails on the file. It costs about 0.55 s.
