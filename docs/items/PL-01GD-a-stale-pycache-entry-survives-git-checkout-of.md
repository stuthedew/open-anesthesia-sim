---
id: PL-01GD
title: A stale __pycache__ entry survives git checkout of an equal-length source edit, so a reverted mutation keeps running and make check reports a failure the source cannot explain
priority: P2
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: Makefile, tests/unit/test_tools_portability.py
added: 2026-09-07
verify: uv run pytest tests/unit/test_tools_portability.py && grep -q 'PYTHONDONTWRITEBYTECODE' Makefile
---

**Problem.** A stale __pycache__ entry survives git checkout of an equal-length source edit, so a reverted mutation keeps running and make check reports a failure the source cannot explain

Observed 2026-09-07 while working `PL-GZP6` (implementing the two required
tests `docs/MODEL.md` names). Mutation-testing the new tissue gate meant
editing `src/anesthesia_sim/core/tissue.py` to swap one `*` for a `/` in
`time_constant_s`, running the test, and reverting with `git checkout`. The
swap leaves the file byte-length unchanged, and CPython's default bytecode
invalidation compares the source's size and mtime against what the `.pyc`
recorded. That was evidently not enough here: after the revert, with `git
status` clean and the correct `*` visible in the file, the interpreter kept
executing the mutated bytecode.

What it cost: `make check` failed on
`test_a_larger_or_more_soluble_tissue_has_a_longer_time_constant` reporting
`tau = 30.0` for a group whose parameters give 480.0, and reporting it
alongside `tissue_blood_partition_coefficient = 4.0`, which is the correct
value and cannot produce 30.0 through the source as written. The same test
had passed minutes earlier in isolation. Two runs were spent before
`find . -name '__pycache__' -prune -exec rm -rf {} +` resolved it and the
value returned to 480.0.

**Why it matters.** The wrong answer is silent and it is confident. A session
that hit this while reverting any source edit would be looking at a red
`make check`, a clean `git status`, and a failure whose numbers are
unreachable from the code in front of it - and the two readings available are
both wrong: that its own new test is broken, or that `main` is red. Either
could be acted on. It also lands squarely on the practice this project asks
for: `.claude/skills/docket/SKILL.md` requires a `verify:` command be watched
failing before it is written down, and mutating source then reverting is how
a session does that.

**Approach.** Undecided, and there are at least three. `PYTHONDONTWRITEBYTECODE=1`
in the `Makefile`'s test targets costs a little startup time and removes the
class outright - it is what this session used for its second, clean pass of the
mutation runs. `python3 -B` at the pytest invocation is the same thing scoped
narrower. `sys.pycache_prefix` or a `--cache-clear`-style step is heavier.
Worth checking first whether this reproduces on a second machine or is
specific to this container's filesystem timestamp granularity, since that
changes which fix is warranted.

**Where.** `Makefile` test targets; `.claude/skills/docket/SKILL.md`'s
"Run it and watch it fail" guidance, which is what leads a session here.

**Done when.** A source edit reverted with `git checkout` cannot leave stale
bytecode executing under the project's own test targets - the cheapest form
being `PYTHONDONTWRITEBYTECODE=1` on the `Makefile` targets that run `pytest`,
which is what this session's second, clean mutation pass used. Confirmed by
running the original reproduction: mutate `time_constant_s`, run the test,
revert, re-run, and see the correct value without clearing `__pycache__` by
hand.

Re-checked 2026-09-12: neither `PYTHONDONTWRITEBYTECODE` nor `python -B` is set
anywhere in the `Makefile` or `pyproject.toml`, so nothing has changed since the
observation and the reproduction still stands as written.
