---
id: PL-921W
title: The formatter target applies to tools/, which must run under bare python3, and nothing guards it the way subprojects/docket/ is guarded
priority: P2
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: tools/ruff.toml, tests/unit/test_tools_portability.py, tests/unit/test_doc_check.py
added: 2026-08-31
verify: uv run pytest tests/unit -k portability
---

**Problem.** `pyproject.toml` sets `target-version = "py314"` for the whole
repository, and `make check` runs `python3 tools/doc_check.py check` with
whatever bare `python3` is on PATH — 3.11 in the web-session container. With
that target, `ruff format` rewrites `except (OSError, subprocess.SubprocessError):`
into PEP 758's unparenthesized form, which 3.11 cannot parse. Observed
2026-08-31 while adding a `try`/`except` to `tools/doc_check.py` under PL-H7XN:
`make fix` produced a `SyntaxError` in a file the suite had just passed.

**Why it matters.** It is not a new hazard: `subprojects/docket/` was broken
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

**Triaged 2026-08-31.** P2, `defect`/`infra`, `dev-tooling`. The widened test
goes in `tests/unit/test_tools_portability.py`, which is what makes the
`verify:` command above select anything: `-k portability` matches a test's
module name as well as its own, so the file name is load-bearing. Whatever is
left of `test_the_tool_parses_under_the_interpreter_that_actually_runs_it` in
`tests/unit/test_doc_check.py` moves there rather than being duplicated.
`subprojects/docket/tests/test_portability.py` is outside the command's scope
(`tests/unit`) and is unaffected.

Not admitted to v0.2.8's frozen list: it completes no entry on it, and
`ROADMAP.md`'s "What the freeze closes, and what it does not" sends a finding
that is neither new scope nor a completion to the queue. The hazard it
describes was *created* by `PL-H7XN`'s fix landing only in `doc_check.py`, so
it is worth doing early in the next release rather than late.
