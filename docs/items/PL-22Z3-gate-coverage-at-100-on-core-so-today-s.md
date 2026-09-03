---
id: PL-22Z3
title: Gate coverage at 100% on core/, so today's saturation cannot silently regress
priority: P2
effort: S
status: done
classes: test, infra
feature: core-guard-coverage
milestone: v0.3.3
touches: Makefile, .github/workflows/quality.yml
added: 2026-09-03
closed: 2026-09-03
pr: 264
verify: uv run pytest tests/unit/test_bootstrap.py && grep -q 'cov-fail-under=100' Makefile && grep -q 'cov-fail-under=100' .github/workflows/quality.yml
---

**Problem.** `pytest-cov` is a declared dev dependency and nothing ever runs
it. `make check` runs a bare `uv run pytest`; `.github/workflows/quality.yml`
runs a bare `uv run pytest`; `[tool.pytest.ini_options] addopts` is `-ra`. So
coverage is measured only when a session asks for it by hand, which is how the
`core-guard-coverage` feature's items came to be written one compartment at a
time.

Measured 2026-09-03 with `--cov-branch` over the whole suite: **every module
under `src/anesthesia_sim/core/` is at 100% of statements and 100% of
branches.** The feature that got it there is 7/9 done. Nothing holds it.

**Why it matters.** Saturated coverage that no gate defends decays silently: a
new branch in a compartment guard ships uncovered, and the first anyone knows
is the next hand-run report. `core/` is the tree `CLAUDE.md`'s safety standard
applies to most directly, and its guards are exactly the code whose uncovered
branch is invisible until it fires in front of a user. The cost of holding the
line now is one flag; the cost of recovering it later is another nine items.

**Decided** (project owner, 2026-09-03): gate at **100% on `core/` only**, no
gate on `app/` or elsewhere. `app/main.py` sits at 48% behind Flet's runtime
and is `PL-NC2P`'s problem; a repository-wide number would either be set low
enough to mean nothing or would block on that item.

**Where.** `Makefile:check`; `.github/workflows/quality.yml`.

**Approach.** Run the gate where gates run:
`uv run pytest --cov=anesthesia_sim.core --cov-branch --cov-fail-under=100`,
as `make check`'s pytest line and as CI's.

**Not in `[tool.pytest.ini_options] addopts`**, which was the first instinct
and is wrong. Coverage of `core/` is the union of everything that exercises
it, so the threshold is only reachable from a whole-suite run - and `addopts`
applies to *every* invocation, including the scoped `uv run pytest
tests/unit/test_tissue.py` that `CLAUDE.md`'s session-efficiency section tells
sessions to use while iterating. Every one of those would fail the gate for a
reason that has nothing to do with the change under it. That is precisely the
check `CLAUDE.md` says to retire: one that fires every run without changing a
decision, training a session to skim the output where a real advisory also
appears.

Two things to get right, both of which have bitten this store before
(`PL-G049`): `--cov=` takes the **dotted module** `anesthesia_sim.core`, never
a path, and the run must be the whole suite. Confirm the flag does not slow
`make check` meaningfully - the suite is 86 s and coverage instrumentation is
the kind of cost that turns a gate into something sessions route around.

`drift.yml` needs no change and should get none: it runs a bare `uv run
pytest` against re-resolved dependencies, and a coverage failure there would
report as a dependency break, which is the opposite of what that workflow is
for.

**The `verify:` command deliberately does not re-run the gate.** Proving the
flag landed in both places is a grep; proving `core/` is at 100% is what the
gate itself does on every `make check` once it exists. Duplicating it would
put a 97 s command in the pool `docket check` waits on, for every session
until this item closes.

**Done when.** A statement or branch newly uncovered in any
`src/anesthesia_sim/core/` module fails `make check` and CI, and the threshold
is written only on the two gate invocations - not in `addopts`, not in a
`[tool.coverage]` table, and nowhere a scoped run would inherit it.

*Amended on closing, 2026-09-03.* This previously ended "and the threshold is
written in exactly one place", which contradicts this item's own `verify:`
command - that command greps for `cov-fail-under=100` in `Makefile` **and** in
`.github/workflows/quality.yml`, because CI mirrors `make check` step by step
rather than calling it. The two are genuinely two places, and the alternative
that would make them one - `fail_under` in `[tool.coverage.report]` - reopens
exactly the trap the "Not in `addopts`" paragraph above rejects, one step
removed: it would apply the threshold to any `--cov` run, including the scoped
one a session makes when coverage is the question. So the duplication is
deliberate and the sentence was wrong, not the approach. Both invocations carry
a comment saying they must stay identical.

**Closed 2026-09-03.** `--cov=anesthesia_sim.core --cov-branch
--cov-fail-under=100` is on `make check`'s pytest line and on CI's. Measured
before wiring it in: every module under `src/anesthesia_sim/core/` is at 100% of
statements and 100% of branches (691 statements, 78 branches, 0 missed), and the
gate costs 92.8 s against 92.4 s for the bare suite - inside the noise, so the
"confirm the flag does not slow `make check` meaningfully" condition is met with
room to spare. `drift.yml` untouched, as specified.

**Landed ahead of `PL-GS5X` deliberately.** That item (replace the operator split
with the exact matrix exponential) adds a hand-rolled `build_system_matrix`,
`matrix_exponential`, `multiply` and `propagate` to `core/`. With the gate in
place first, the new solver has to arrive fully covered; landing the gate
afterwards would have measured against code that may already have dropped below
the line, turning a one-flag item into a coverage chase.
