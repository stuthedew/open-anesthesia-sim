"""Ambient git configuration no test tree in this repository may read.

`GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` are set to `/dev/null`, which git
documents as the value that makes it read no configuration at that level (git
2.32 and later). Tests under `subprojects/docket/tests/` build a scratch
repository with real git per test, because what is under test is largely what
git reports, and `tests/unit/`'s hook tests run git too - so whatever the
developer keeps in `~/.gitconfig` reaches all of it, and one ordinary setting
there changes what the suite costs for reasons nothing in the tests explains.
`commit.gpgsign = true` with `gpg.format = ssh` costs 72.7 ms per commit
against 5.1 ms unsigned; over the 563 commits the `docket` tree makes that is
40.9 s of a 60.4 s run, which these two lines cut to 2.9 s of 21.5 s with no
test changed (`PL-YRYR`, measured 2026-09-21).

Speed is the half that can be measured. The half that matters more is that a
signing key held on hardware, or behind a passphrase, does not make the suite
slow - it makes `git commit` block on a prompt or fail outright, and every test
that needs history fails with it, on a machine where nothing is wrong. A suite
that builds real repositories has to own their configuration; reading the
developer's is how it becomes environment-dependent without anyone choosing
that, and the failure then arrives on someone else's machine.

Assignment rather than `setdefault`, unlike `QT_QPA_PLATFORM` in
`tests/conftest.py`: there a developer with a display may legitimately want
their own value, whereas here a test repository that reads an outside config is
the defect, so there is no version of it to preserve.

At the repository root rather than in each tree, for two reasons. One rule
covers both trees and `pytest` resolves `rootdir` here however it is invoked -
including from inside `subprojects/docket/`, whose own `pyproject.toml`
declares no pytest section, so the walk continues up to this one. And
`tools/ignore_check.py` type-checks `tests` and `subprojects/docket/tests` in a
single mypy invocation, where a second file named `conftest` in those trees is
a duplicate-module error that stops mypy before it evaluates anything
(`PL-CR36`). This file sits outside both, so it cannot collide.
"""

import os

os.environ["GIT_CONFIG_GLOBAL"] = "/dev/null"
os.environ["GIT_CONFIG_SYSTEM"] = "/dev/null"
