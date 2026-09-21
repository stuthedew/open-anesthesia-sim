"""Ambient git configuration the repositories built in this tree must not read.

`GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` are set to `/dev/null`, which git
documents as the value that makes it read no configuration at that level (git
2.32 and later). Almost every test here builds a scratch repository with real
git, because what is under test is largely what git reports - so whatever the
developer has in `~/.gitconfig` reaches those repositories, and one ordinary
setting there changes what the suite costs for reasons nothing in the tests
explains. `commit.gpgsign = true` with `gpg.format = ssh` costs 72.7 ms per
commit against 5.1 ms unsigned; over the 563 commits this tree makes that is
40.9 s of a 60.4 s run, which these two lines cut to 2.9 s of 21.5 s with no
test changed (`PL-YRYR`, measured 2026-09-21).

Speed is the half that can be measured. The half that matters more is that a
signing key held on hardware, or behind a passphrase, does not make this suite
slow - it makes `git commit` block on a prompt or fail outright, and every test
that needs history fails with it, on a machine where nothing is wrong. A suite
that builds real repositories has to own their configuration; reading the
developer's is how it becomes environment-dependent without anyone choosing
that, and the failure arrives on someone else's machine.

Assignment rather than `setdefault`, unlike `QT_QPA_PLATFORM` in the
repository's own `tests/conftest.py`: there a developer with a display may
legitimately want their own value, whereas here a test repository that reads an
outside config is the defect, so there is no version of it to preserve.

This tree carries its own copy rather than inheriting one from the repository
root because `subprojects/docket/` is a standalone package - `pytest` run from
inside it has to get the same isolation as `pytest` run from the root.
"""

import os

os.environ["GIT_CONFIG_GLOBAL"] = "/dev/null"
os.environ["GIT_CONFIG_SYSTEM"] = "/dev/null"
