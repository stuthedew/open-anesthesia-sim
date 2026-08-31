---
id: PL-921W
title: The formatter target applies to tools/, which must run under bare python3, and nothing guards it the way subprojects/docket/ is guarded
status: untriaged
added: 2026-08-31
---

**Problem.** The formatter target applies to tools/, which must run under bare python3, and nothing guards it the way subprojects/docket/ is guarded

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `pyproject.toml` sets `target-version = "py314"` for the whole
repository, and `make check` runs `python3 tools/doc_check.py check` with
whatever bare `python3` is on PATH — 3.11 in the web-session container. With
that target, `ruff format` rewrites `except (OSError, subprocess.SubprocessError):`
into PEP 758's unparenthesized form, which 3.11 cannot parse. Observed
2026-08-31 while adding a `try`/`except` to `tools/doc_check.py` under PL-H7XN:
`make fix` produced a `SyntaxError` in a file the suite had just passed.

**Why it matters, and why it is not new.** `subprojects/docket/` was broken
this exact way once. It now carries its own `ruff.toml` pinned to `py311` and
`tests/test_portability.py`, whose docstring names the same rewrite.
`tools/doc_check.py` makes the identical promise — its module docstring says
"standard library only ... so this runs in a bare checkout exactly as it runs
in CI" — and has neither the pinned target nor the test. The same shape as
`PL-J295` (the tag reader had the pull-request reader's exposure and was
missed): a hazard was found, fixed where it fired, and left in the second
place it applies.

The failure is quiet in the direction that matters. The suite runs under the
project virtualenv on 3.14 and passes; only the bare-`python3` invocation
fails, and a session that runs `pytest` but not `make check` sees nothing.

**Where.** `pyproject.toml` (`[tool.ruff] target-version`), `tools/`, and
`subprojects/docket/ruff.toml` as the pattern to copy.

**Already done under PL-H7XN, and why it is not enough.** `doc_check.py` names
its except-tuple as `GIT_UNAVAILABLE` so the formatter cannot rewrite it, and
`tests/unit/test_doc_check.py` asserts the file parses at
`feature_version=(3, 11)`. Both are specific to that one file and to that one
construct: a second tool under `tools/`, or a second 3.14-only construct in
this one, is exposed again.

**Approach.** A `tools/ruff.toml` with `target-version = "py311"` is the fix
that removes the hazard rather than detecting it, matching what
`subprojects/docket/` already does; the floor wants declaring somewhere
readable, since `tools/` has no `pyproject.toml` of its own to hold
`requires-python`. Then widen the portability assertion from `doc_check.py` to
every file under `tools/`, so a new tool inherits the guard.

**Done when.** `ruff format` cannot emit syntax that bare `python3` rejects for
anything under `tools/`; a test proves it for every file there, not one; and
the declared floor is written down where the next person will find it.
