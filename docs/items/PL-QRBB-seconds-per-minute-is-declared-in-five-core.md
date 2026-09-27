---
id: PL-QRBB
title: SECONDS_PER_MINUTE is declared in five core modules, one of which no longer uses it, and a reference test borrows it to turn minutes into hours
status: untriaged
added: 2026-09-27
---

**Problem.** SECONDS_PER_MINUTE is declared in five core modules, one of which no longer uses it, and a reference test borrows it to turn minutes into hours

**Why it matters.** Not because the copies can drift. A minute is sixty
seconds by definition (SI Brochure, 9th edition, Table 8), so five copies
cannot disagree, and `PL-TCW5` said as much when it single-sourced
`FLOW_FRACTION_TOLERANCE` and left this one. The costs are elsewhere, and each
is in the tree now:

1. **An orphan.** `PL-SM5V` (#1191, 2026-09-27) moved the four
   litres-per-minute to litres-per-second conversions out of
   `core/uptake_system.py` into `core/governing_equations.py`, which declared a
   copy of its own. `uptake_system.py`'s copy has no use left in its module
   and survives only because two reference tests import it from there. `main`
   went green with it, so no configured check reports an unused module-level
   name.
2. **No home.** Tests import the constant from `core/uptake_system.py` (two
   files) and `core/governing_equations.py` (one), and declare their own in
   `tests/reference/test_coupled_dynamics.py` and
   `tests/benchmarks/frame_cost.py`. `from anesthesia_sim.core.uptake_system
   import SECONDS_PER_MINUTE` invites a reader to think the value belongs to
   the uptake system.
3. **It grows by copying.** Four copies when `PL-TCW5` counted them on
   2026-09-02, five now: each new module copies its neighbour's header.
4. **A borrowed name.** `tests/reference/test_late_washout_against_published_fits.py`
   divides by `SECONDS_PER_MINUTE` to turn minutes into hours in
   `hours_at_which_terms_are_equal`, `_crossing_hours` and
   `test_the_fourth_compartment_is_the_largest_term_over_the_recorded_hours`,
   and the last does the same conversion again in the next statement as a bare
   `ELIMINATION_DURATION_MIN / 60`. The number is right and the name is wrong,
   in a test whose job is to be read against a paper. Consolidating does not
   fix this one; a constant with the right name does. (`_metabolise` in the
   same file uses it correctly.)

`_MILLISECONDS_PER_SECOND` repeats the pattern in the interface:
`app/run_view.py`, `app/simulation_view.py` and
`tests/benchmarks/frame_cost.py` each declare it.

None of this changes a number, and it is not a safety finding. The hazard a
factor of sixty carries is a conversion applied twice, not at all, or at the
wrong point - a sixty-fold error. The unit-suffixed names (`_l_min`, `_l_s`,
`_s`) and `PL-SM5V`'s single derivation of each per-second flow are what guard
that, and the number of declarations reaches neither.

**Where.** `src/anesthesia_sim/core/`: `blood.py`, `tissue.py`, `circuit.py`,
`governing_equations.py`, `uptake_system.py`. `src/anesthesia_sim/app/`:
`run_view.py`, `simulation_view.py`. Tests:
`tests/unit/test_governing_equations.py`,
`tests/reference/test_published_wash_in_and_elimination.py`,
`tests/reference/test_late_washout_against_published_fits.py`,
`tests/reference/test_coupled_dynamics.py`, `tests/benchmarks/frame_cost.py`.
`docs/ARCHITECTURE.md` for the new module's entry.

**Decision needed.** Whether to consolidate, and how far. Put to the project
owner 2026-09-27, who raised it as a general aversion to duplicate
declarations, and not yet answered.

**Recommendation.** Consolidate, as follows.

1. A leaf module, `core/units.py`, declaring `SECONDS_PER_MINUTE`,
   `MINUTES_PER_HOUR` and `MILLISECONDS_PER_SECOND` as `Final`, each with a
   docstring in the style of `PERCENT_PER_UNIT_FRACTION`: a definition, so no
   provenance note. It imports nothing from the package, so no module
   importing it can form a cycle. It also takes a line in
   `docs/ARCHITECTURE.md`'s package map, which `tools/doc_check.py` holds to
   the tree on disk in both directions.
2. The four core modules that use the constant import it; their copies go,
   and so does `uptake_system.py`'s orphan.
3. The two interface modules import `MILLISECONDS_PER_SECOND` in place of
   their private copies.
4. Tests import from `core/units.py`, with one exception:
   `tests/reference/test_coupled_dynamics.py` keeps its own copy, with a
   comment saying why. Its `_build_derivative` writes every equation out from
   `docs/MODEL.md` rather than calling the implementation, "which is what makes
   agreement evidence"; importing the core's constant would have it check the
   core against itself on exactly this factor (`CLAUDE.md`: "independently
   calculated test vectors").
5. The three minutes-to-hours conversions and the bare `/ 60` in the
   late-washout test use `MINUTES_PER_HOUR`.

Left alone, deliberately: `PERCENT_PER_UNIT_FRACTION`, already single and
beside its two conversions in `core/concentration.py`; the bare `3600.0` and
`60.0` in `app/formatting.py`'s `_duration_components`,
`format_supported_run_length` and `core/supported_ranges.py`'s
`require_supported_run_length`, which are arithmetic whose meaning is plain
where it stands rather than declarations; and literal `60.0` in test expected
values, where independence from the implementation is the point. No guard
test: what it would stop is harmless by the argument above, so it could not
change a decision.

`PL-F08Y` (the 24-hour washout tests' recompute cost) holds a live claim on
the late-washout test file. The edits here to that file are one import and
three names, so whichever lands second takes a small merge; neither waits on
the other, since a shared file is not a concurrency refusal (`PL-VRMK`).

**Done when.** `grep -rnE '^_?(SECONDS_PER_MINUTE|MINUTES_PER_HOUR|MILLISECONDS_PER_SECOND)\b[^=]*=[^=]' src tests`
returns `core/units.py` and the one commented oracle in
`tests/reference/test_coupled_dynamics.py`; no test's expected value changes;
the full suite passes.

**Decided 2026-09-27: build it as recommended** (project owner, 2026-09-27,
ratified, over leaving the five copies in place as `PL-TCW5` did, and over
consolidating every copy, the independent oracle's included).
