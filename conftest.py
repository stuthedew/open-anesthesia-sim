"""Process settings every pytest run in this repository takes, however it is started.

**Git configuration no test tree may read.**
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

**No bytecode written, so a restored source is the one that runs** (`PL-0MLZ`).
CPython accepts a cached `.pyc` when the source's size, and its mtime truncated
to the whole second, match what the cache recorded: in
`importlib._bootstrap_external`, `SourceLoader.get_code` takes `int()` of the
mtime and `_validate_timestamp_pyc` compares the two. So an equal-length edit
that is compiled and then reverted inside one second leaves a cache that
validates against the reverted file, and the next run executes the edit the
file no longer contains. That is the mutation test's own rhythm: measured
2026-09-27, 11 of 12 cycles of mutating
`src/anesthesia_sim/core/alveolar.py`'s `gas_volume_l` from 2.5 to 2.6,
importing it, copying the original back and importing again ran 2.6 while the
file said 2.5. It fails in the direction that costs most - a test that looks
as if it catches a mutation when what ran was another build - and `PL-01GD`
met it in `make check`.

`sys.dont_write_bytecode` stops this process writing a cache, and
`PYTHONDONTWRITEBYTECODE` reaches the interpreters the suite starts - the
hooks, `tools/` and `bin/docket` runs under test. The `Makefile` exports the
same variable to its recipes, but a `verify:` command, a session iterating and
CI all run `pytest` without `make`, and uv has no setting that exports a
variable: uv 0.12.19 refuses `env` and `env-file` under `[tool.uv]` as unknown
fields and reads a `.env` only when told to. Here it follows every `pytest`
run and nothing else, so the app's own startup keeps its cache.

It stops a write and not a read: a cache written by something other than a
test run, from source mutated and restored inside one second, still shadows
the restored file.

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
import sys

os.environ["GIT_CONFIG_GLOBAL"] = "/dev/null"
os.environ["GIT_CONFIG_SYSTEM"] = "/dev/null"

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
