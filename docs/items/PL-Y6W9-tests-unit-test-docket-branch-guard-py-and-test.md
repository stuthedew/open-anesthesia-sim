---
id: PL-Y6W9
title: tests/unit/test_docket_branch_guard.py and test_docket_digest_hook.py run the hooks under PATH=/usr/bin:/bin:/usr/local/bin, so on macOS bin/docket runs under the 3.9.6 system python3, fails on datetime.UTC, and eight tests are red on the owner's own machine while green in CI
status: untriaged
added: 2026-09-14
---

**Problem.** tests/unit/test_docket_branch_guard.py and test_docket_digest_hook.py run the hooks under PATH=/usr/bin:/bin:/usr/local/bin, so on macOS bin/docket runs under the 3.9.6 system python3, fails on datetime.UTC, and eight tests are red on the owner's own machine while green in CI

**Found 2026-09-14** running `make check` on the project owner's Mac while
working `PL-9KDK`. Both test files run the hook with a fixed environment -
`PATH=/usr/bin:/bin:/usr/local/bin` - and the hook's shim execs `bin/docket`,
which picks up `/usr/bin/python3`. On macOS that is the Command Line Tools'
3.9.6, and `subprojects/docket/src/docket/render.py` imports `datetime.UTC`
(3.11+), so `bin/docket` exits 1 with an `ImportError`; the hook swallows it
and exits 0 with empty stdout, exactly as its own contract says it must, and
the eight tests that expect JSON or a line fail on `''`. On ubuntu-latest
`/usr/bin/python3` is 3.12 and the same tests pass, so the suite is red only
where the owner runs it.

**Why it matters.** `make check` is what every session runs before committing,
and a suite that is red for a reason unrelated to the work trains the reader to
skim past the failure block - the same habit `CLAUDE.md` names for an advisory
nobody acts on. The fix is either to put the interpreter under test on the
restricted PATH (a symlink dir in `tmp_path` pointing at `sys.executable`), or
to have the hook prefer the same interpreter the tests run under; the first
keeps the hook's promise of running under whatever `python3` a bare checkout
has.

**Done when.** The eight tests pass on a Mac whose `/usr/bin/python3` is 3.9,
and still exercise the hook through `bin/docket` rather than bypassing it.
