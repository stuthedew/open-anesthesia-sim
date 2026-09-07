---
id: PL-SHTR
title: docket verify does not set LANDED_GUARD, so an item whose verify: runs docket check --verify replays the whole store one level down
priority: P3
effort: S
status: ready
classes: infra
feature: dev-tooling
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-07
verify: uv run pytest subprojects/docket/tests/test_verify.py && grep -q 'def test_a_nested_docket_check_from_verify_declines' subprojects/docket/tests/test_verify.py
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
