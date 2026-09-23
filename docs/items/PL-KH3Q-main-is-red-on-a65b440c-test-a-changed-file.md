---
id: PL-KH3Q
title: main is red on a65b440c: test_a_changed_file_list_git_does_not_answer_declines_the_replay, added by #933 (PL-9RFP), asserts git's 'index file corrupt' but check now prints #930's (PL-NGBM) '--no-git asks git nothing' sentence, because #933's CI ran on a base without #930
priority: P2
effort: S
status: done
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/tests/test_cli.py, docs/items/PL-99YZ-three-sessions-opened-three-pull-requests-for.md
added: 2026-09-23
closed: 2026-09-23
verify: uv run pytest -q subprojects/docket/tests/test_cli.py -k test_a_changed_file_list_git_does_not_answer_declines_the_replay
---

**Problem.** main is red on a65b440c: test_a_changed_file_list_git_does_not_answer_declines_the_replay, added by #933 (PL-9RFP), asserts git's 'index file corrupt' but check now prints #930's (PL-NGBM) '--no-git asks git nothing' sentence, because #933's CI ran on a base without #930

**Found 2026-09-23 from the session-start digest.** main's quality run #2890
(https://github.com/stuthedew/open-anesthesia-sim/actions/runs/35804355265)
failed 1 of 4252: `subprojects/docket/tests/test_cli.py::test_a_changed_file_list_git_does_not_answer_declines_the_replay`.
The test runs `check --verify --verify-base <base> --items <store>` with
`cli.changed_paths` patched to raise `GitUnanswered("... index file corrupt")`,
and asserts that text reaches the output. The output instead carries the
sentence `subprojects/docket/src/docket/cli.py` builds at line 671 - "`--no-git`
asks git nothing, so that was not read" - which #930 (`PL-NGBM`, merged 19:49
-0500) introduced. #933 (`PL-9RFP`, merged 19:58 -0500) added the test on a
base without #930, so each pull request was green and the pair is red. Neither
change is wrong on its own evidence; the fix decides which path the test's
invocation should take under #930's `Invocation`, and whether a store
addressed by `--items` alone now resolves to no-git where it should not.

Every open branch inherits the red at `make check` and in pull-request CI, so
this outranks the queue until it lands, and one session should hold it: claim
it with an empty commit before any work (`PL-99YZ` is the three-duplicate-fixes
precedent).

**Resolved 2026-09-23. The fix landed in #934 (`8aa8ccf2`), not on this
branch.** The invocation was wrong, not the test or the code. `_run` in
`test_cli.py` appends `--no-git`, and since #930 that flag is `Invocation.git`
being `None` and nothing else (`cli._invocation`). So `cmd_check` takes its
no-git branch and declines the scoped replay before `changed_paths`, the read
the test patches, is ever asked. That decline also prints "not checked", which
is why only the test's last assertion caught it. That answers the brief's
second question: a store addressed by `--items` alone does not resolve to
no-git. The helper passed the flag.

The fix moves the one call to `_run_with_git`, which #930 added for exactly this
case ("`_run` for a test of a git read itself"). The two neighbouring replay
tests already use it. `PL-XYQW`'s session wrote it first, as `795ebbf6` at 01:17
UTC. #934 (`PL-19T3`) ported that commit and merged at 01:35. This branch made
the same change as `6e8331f5` and dropped it for main's copy when it merged the
base. `PL-99YZ` records the three fixes.

No other test from #933, or from #931 and #932 (merged after #930), runs a git
read under `--no-git`. #933's `test_verify.py` additions call `verify`
directly. Its renamed outside-a-repository test already calls `_run_with_git`,
taken from #930's side of the merge.

Evidence, taken on this branch's copy, which makes the same call with the same
arguments as main's: the test fails on unmodified `a65b440c` with CI's
assertion error. It passes with the fix. It fails again when `cmd_check`'s
`declined = declined or str(silence)` becomes `pass`, which reads the
unanswered half as "nothing changed", as the code did before #933. So the test
now exercises the half it is named for. The recurrence is `PL-Z0SM`'s to count.
