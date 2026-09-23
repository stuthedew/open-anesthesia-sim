---
id: PL-KH3Q
title: main is red on a65b440c: test_a_changed_file_list_git_does_not_answer_declines_the_replay, added by #933 (PL-9RFP), asserts git's 'index file corrupt' but check now prints #930's (PL-NGBM) '--no-git asks git nothing' sentence, because #933's CI ran on a base without #930
status: untriaged
added: 2026-09-23
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
