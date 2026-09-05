---
id: PL-W6NY
title: test_verify.py spends more on _repo's five git subprocesses per test than on sleeping, and 63 other tests pay the same fixture
status: untriaged
feature: dev-tooling
touches: subprojects/docket/tests/test_verify.py
added: 2026-09-05
---

**Problem.** `PL-VJ7W` was filed against the `sleep` durations in
`subprojects/docket/tests/test_verify.py`, on the reading that "nearly all" of
the file's 24 s is deliberate sleeping. Measured 2026-09-05 with
`--durations`, that is about half of it:

| | Serial |
| --- | --- |
| the five sleep-driven tests | 10.5 s |
| the other 59 tests | ~12 s |
| **file total** | **22.5 s** |

Those 59 tests do not sleep. Each calls `_repo(tmp_path)`, which runs five git
subprocesses - `init`, two `config`s, `add`, `commit` - and writes four files,
for a repository most of them use only as a working directory to run `true`
in. That is roughly 320 git processes across the file.

**Why it matters.** It is the larger half of the cost `PL-VJ7W` set out to
reduce, and unlike the sleeps it is not holding any assertion open: nothing in
these tests is about git. It also sets a per-test floor that every test added
to the file pays.

**Where.** `subprojects/docket/tests/test_verify.py`, `_repo` at lines 48-61
and its 64 call sites.

**The catch, and why this is filed rather than done.** A session-scoped
fixture is the obvious move and is not obviously safe: some tests in this file
commit into the repository they are given, so a shared one would carry state
between tests and the order-dependence would surface as a flake later, in a
different test, which is worse than the 12 s. The candidates worth weighing
are a template repository copied per test (`shutil.copytree` against five git
processes), `git init` alone for the tests that never commit, or leaving it
alone.

Weigh it against `.claude/rules/apparatus-standard.md` before building: this
is apparatus, the bar is working reliably and staying streamlined, and a
fixture that trades 12 s for an intermittent failure is a bad trade at any
price.

**Found while working `PL-VJ7W`** (trim the file's non-load-bearing sleeps),
which measured the file to decide which sleeps were real and found half the
cost was somewhere else.
