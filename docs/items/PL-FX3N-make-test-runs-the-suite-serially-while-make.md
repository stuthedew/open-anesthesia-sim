---
id: PL-FX3N
title: make test runs the suite serially while make check runs it at -n auto, so the target a session uses while iterating is the slow one
priority: P2
effort: S
status: done
classes: perf, infra
feature: dev-tooling
touches: Makefile, README.md
verify: python3 tools/doc_check.py check && grep -qE 'uv run pytest -n auto$' Makefile
added: 2026-09-04
closed: 2026-09-04
---

**Problem.** `PL-WCZV` put `-n auto` on `make check`'s `pytest` line and on the
CI step. `make test` - "pytest only, without the coverage gate", the target a
session runs while iterating - was left bare, so it still runs serially. On a
four-core box that is roughly 78 s against 27 s for the same tests.

**Why it matters.** The slow one is the one a session reaches for most, so the
saving is missed exactly where iteration cost is felt. It is also a third place
the flag has to agree with the other two, which is the invariant `PL-D3M2`
already says nothing holds.

**Why it was left rather than fixed.** `PL-KCQ7`'s session added it, then
dropped the edit when `PL-WCZV` turned out to have landed on `main` in parallel:
`make test` was outside what the owner approved, and quietly widening a branch
that had just collided was the wrong move twice over.

**Not automatic.** The `check`-target reasoning does not transfer unexamined -
`-n` interleaves output and defeats `-x` and `pdb`, which is part of what
`make test` is for. Consider whether the answer is `-n auto` on the target, a
`make test-fast`, or leaving it and saying why in the target's comment.

**Where.** `Makefile`'s `test` target; `README.md`'s target listing if the
answer changes what it does.

**Done when.** `make test` either runs across cores or carries a comment saying
why it deliberately does not.

**Worked.** `-n auto` on the `test` target, with the reasoning in the comment
above it. Measured on this container, four cores, 1230 tests, the same suite
both ways:

| | wall clock | result |
| --- | --- | --- |
| serial (before) | **88.5 s** | 1230 passed |
| `-n auto` | **31.8 s** | 1230 passed |

2.8x, matching the 2.85x `PL-WCZV` measured on the `check` line; the container
was slower today than it was on 2026-09-03, so the ratio is the number that
carries rather than either absolute.

**The "not automatic" objection did not survive being checked, and it was
wrong in two independent ways.** The brief held that `-n` "defeats `-x` and
`pdb`, which is part of what `make test` is for".

*First, the recipe takes no arguments.* `make test` is `uv run pytest` and
nothing else - there is no `ARGS=` pass-through - so `-x` and `--pdb` could
never be given to it. A session debugging is already running `uv run pytest -x
tests/unit/test_x.py` directly, which this change does not touch. The target
that was being protected for debugging cannot debug.

*Second, `-n auto` specifically does not defeat the debugger anyway.* Given
`--pdb`, xdist sets `numprocesses = 0` and `dist = "no"` and runs serially
(`xdist/plugin.py`, `pytest_cmdline_main`, the `numprocesses in ("auto",
"logical")` branch); it is a pinned width that raises `--pdb is incompatible
with distributing tests; try using -n0 or -nauto`. Confirmed against
pytest 9.1.1 / pytest-xdist 3.8.0: `-n 2 --pdb` is a usage error, `-n auto
--pdb` drops into the debugger exactly as a serial run does. So `auto` is the
one width that is safe to copy into a direct invocation, which is a second
reason to prefer it over a number beyond the machine-portability argument
`PL-WCZV` gave.

`-x` does work under `-n auto`, at a cost worth stating rather than hiding:
the run stops, but the in-flight workers finish their current chunk first, so
more tests run before it stops (probed at 400 tests: 8 serially against 139).
The failure is still reported, and with `--dist load` the ordering of failure
reports across workers is not guaranteed to be file order. That cost is
theoretical here for the reason above - it cannot reach this target.

**Why not `make test-fast`.** A second target leaves the default slow, and the
default being slow is the entire complaint: nobody types the longer name of the
faster thing. It would also give the flag a fourth home.

**What it does to `PL-D3M2`,** which is still `needs-decision` and whose subject
is exactly this kind of drift. There are now two `uv run pytest` lines in the
`Makefile`, so "the Makefile's pytest line" no longer identifies one. They are
not two legs of one invariant: `check`'s line must stay byte-identical to
`.github/workflows/quality.yml`'s step because it is the coverage gate run
twice, while `test`'s shares the flag and nothing else - no `--cov`, no
threshold, no obligation to the workflow. Drift between `check` and CI voids a
guarantee silently; drift between `check` and `test` only makes one target
slow. `PL-D3M2` has been amended to say so, so whatever rule it lands anchors
to the `check` recipe rather than to a pattern that now matches twice.

`drift.yml`'s two bare `uv run pytest` invocations are untouched and stay that
way, for the reason `quality.yml`'s comment already records under `PL-22Z3`.
