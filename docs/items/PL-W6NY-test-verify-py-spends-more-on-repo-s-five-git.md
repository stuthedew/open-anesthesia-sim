---
id: PL-W6NY
title: test_verify.py spends more on _repo's five git subprocesses per test than on sleeping, and 63 other tests pay the same fixture
priority: P3
effort: S
status: ready
classes: session-cost, infra
feature: dev-tooling
touches: subprojects/docket/tests/test_verify.py
added: 2026-09-05
not-delegable: both outcomes are judgments a command cannot hold. The suite passes today, so it proves nothing about whether a shared or copied fixture has introduced order-dependence - which is the risk the brief says makes the obvious move unsafe, and which surfaces later, in a different test, as a flake. The other outcome is a timing measurement recorded with the reason the fixture was left alone, and a threshold assertion tight enough to discriminate 12 s of git subprocesses would itself flake on a slower runner. `.claude/rules/apparatus-standard.md` is the bar being weighed against, and it is prose.
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

**Done when.** The file's per-test fixture cost has been measured again after a
deliberate choice among the three candidates, and the outcome is written down
either way. If the fixture changes, `--durations` shows the ~12 s of non-sleep
cost reduced, every test in the file still passes when run alone and in a
shuffled order, and no test that commits into its repository can see another
test's commits. If it does not change, the reason sits in a comment on `_repo`
— that the five subprocesses are the price of per-test isolation and that a
shared fixture was weighed against `.claude/rules/apparatus-standard.md` and
rejected — so the next session to measure this file does not re-derive it.

**Triaged as a task rather than a decision, 2026-09-06.** The brief's three
candidates include "leave it alone", which reads like a question for the owner
and is not one: it is an apparatus test fixture, and the brief itself directs
the weighing to `.claude/rules/apparatus-standard.md`, which is addressed to
whoever builds it. The owner is owed the outcome, not the choice.
