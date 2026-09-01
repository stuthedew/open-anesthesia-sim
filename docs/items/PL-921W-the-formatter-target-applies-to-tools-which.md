---
id: PL-921W
title: The formatter target applies to tools/, which must run under bare python3, and nothing guards it the way subprojects/docket/ is guarded
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
touches: tools/ruff.toml, tests/unit/test_tools_portability.py, tests/unit/test_doc_check.py
added: 2026-08-31
verify: uv run pytest tests/unit -k portability
closed: 2026-09-01
commit: 64bcd1e
pr: 141
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

**Admitted to v0.2.8's frozen list, 2026-08-31, reversing the paragraph
above.** The reassessment that added it applied the scope test rather than the
completion rule: `ROADMAP.md`'s "What the freeze closes" now says that a
defect in machinery the release's goal names is inside the frozen scope
however late it is found, and the lint gate is one of the six pieces that goal
names. The paragraph above is kept rather than deleted because its reasoning
was sound about the rule it was applying — the rule was the narrow one.

**Done 2026-09-01.** `tools/ruff.toml` extends the repository's rules and
overrides `target-version` to `py311`, the shape `subprojects/docket/ruff.toml`
already uses, so the formatter can no longer emit syntax bare `python3`
rejects for anything under `tools/`. Verified both ways before and after: at
the repository's `py314` target `ruff format` rewrote a probe file's
`except (OSError, subprocess.SubprocessError):` into PEP 758's unparenthesized
form; with the pin in place it left the same file unchanged.

The floor is no longer a number chosen in `tools/`. `doc_check.py` imports
`docket.roadmap`, so the oldest interpreter these tools can run under is
whatever `subprojects/docket/pyproject.toml` declares in `requires-python`, and
`tests/unit/test_tools_portability.py` reads it from there rather than
declaring a third copy - which is the drift that produced this item.

That file carries the widened guard: the formatter target must equal the
declared floor, `tools/` must be non-empty, and *every* file under it must
parse at the floor, so a second tool inherits the guard without anybody
remembering to extend it. `test_the_tool_parses_under_the_interpreter_that_actually_runs_it`
and its `BARE_PYTHON_FLOOR` constant moved out of `tests/unit/test_doc_check.py`
rather than being duplicated. Confirmed the widened assertion still fires: a
probe file under `tools/` carrying the unparenthesized form failed
`test_every_tool_parses_under_the_interpreter_that_actually_runs_it`.

The floor is written down twice more, for the two readers who would look:
`pyproject.toml` now says beside `target-version = "py314"` that two subtrees
override it and why, and `docs/ARCHITECTURE.md`'s "Developer tooling" section
states the 3.11 floor, where it comes from, and what enforces it.

`GIT_UNAVAILABLE` and `UNREADABLE` in `doc_check.py` are left named. They are
no longer load-bearing against the formatter, but the names read better than
the tuples did and removing them would be an unrelated change.
