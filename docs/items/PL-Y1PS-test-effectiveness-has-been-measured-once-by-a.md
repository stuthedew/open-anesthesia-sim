---
id: PL-Y1PS
title: Test effectiveness has been measured once, by a one-off mutation run whose recipe and baseline live nowhere durable, so it cannot be re-run or compared: record the mutmut 3.8.0 configuration, its pitfalls and the 2026-10-17 baseline (2619 mutants, 279 unit-tier survivors, about 88% killed), and propose diff-scoped mutation rather than whole-tree runs
priority: P3
effort: M
status: ready
classes: infra
feature: test-effectiveness-measurement
touches: Makefile, pyproject.toml, uv.lock, .gitignore, tools/diff_mutation.py, tests/unit/test_diff_mutation.py, tests/unit/test_line_splits.py, docs/mutation-testing.md, docs/apparatus.md, docket.toml, .claude/rules/test-oracles.md, .claude/skills/docket/modes/close-out.md
added: 2026-10-17
payoff: the functions a pull request changes can be mutation-tested in minutes and compared with the 2026-10-17 baseline, so whether the tests catch a wrong value is measured rather than assumed
verify: grep -q 'mutmut' Makefile
---

**Problem.** Test effectiveness has been measured once, by a one-off mutation run whose recipe and baseline live nowhere durable, so it cannot be re-run or compared: record the mutmut 3.8.0 configuration, its pitfalls and the 2026-10-17 baseline (2619 mutants, 279 unit-tier survivors, about 88% killed), and propose diff-scoped mutation rather than whole-tree runs

**What this item is.** A record of how the 2026-10-17 audit measured test
effectiveness with mutation testing, the pitfalls it hit, and the numbers it
got, so that a later session can re-run it and compare. It also carries one
proposal: run mutation on what a pull request changes rather than on the
whole tree, as a measurement rather than a score to reach.

**Decision.** The project owner approved diff-scoped mutation as a
measurement (project owner, 2026-10-17, ratified, over leaving the recipe as a
one-off record and over a whole-tree mutation score as a target). Where the
recipe lives, and whether it runs as a make target or a CI job, is this item's
design work. The capture said this fell under `CLAUDE.md`'s pause on new
workflow mechanisms. That was wrong: the pause applies only while a
workflow-lane head carries `generator: live`, and on 2026-10-17 the only head
that `bin/docket generators` marked still generating was `PL-X7D5`, a
product-lane head (`PL-3KMD`).

**Why it matters.** The 2026-10-17 run is the only measurement of how many
injected faults this suite catches. Without a recorded recipe nobody can run
it again, so no later change to the tests can be shown to have helped. A
diff-scoped run would also put the question to each pull request while its
author still has the change in mind.

**Why mutation testing alone is not enough.** The audit's answer to the
owner's question was no, for four measured reasons. A high mutation score
cannot see self-derived pins, errors that the specification and its oracle
share, wrong data files (mutmut does not mutate JSON), or a test that can fail
only when its neighbour does. The other items in this capture came from the
methods beside mutation: fault injection, stored-value perturbation, oracle
classification and regression-test replay. Petrović et al. found that about
30% of high-priority real bugs at Google were coupled to no generated mutant
(ICSE 2021, pp. 910-921, doi:10.1109/ICSE43902.2021.00087).

**The recipe.**

- mutmut 3.8.0 (PyPI, released 2026-09-12), installed in a scratch virtualenv.
  It is not in the project's dev group.
- A `[tool.mutmut]` table in a copy of `pyproject.toml`, with `source_paths`
  set to `src/` and `only_mutate` set to `core/*` plus `app/formatting.py`,
  `app/chart_time_base.py`, `app/wash_in.py` and `app/run_series.py`.
- The tests are these 33 simulator unit-test files under `tests/unit/`:
  `test_agent_simulation_validation`, `test_alveolar`, `test_blood`,
  `test_chart_frame`, `test_chart_time_base`, `test_checked_number`,
  `test_circuit`, `test_compartment_primitives`, `test_compartment_selection`,
  `test_concentration`, `test_control_timeline`,
  `test_core_constant_provenance`, `test_dashboard_frame`, `test_exceptions`,
  `test_exponential_approach`, `test_formatting`, `test_governing_equations`,
  `test_matrix_exponential`, `test_parameters`, `test_patient`,
  `test_playback`, `test_resume_at`, `test_run_definition`, `test_simulation`,
  `test_simulation_step`, `test_state_capture`, `test_supported_range_edges`,
  `test_supported_ranges`, `test_tissue`, `test_units`,
  `test_uptake_system_failure`, `test_validation` and `test_wash_in`.
- Set `process_isolation = "forkserver"` and `forkserver_warmup = "none"`.
- Deselect `tests/unit/test_supported_range_edges.py::test_each_guard_admits_only_what_its_functions_compute`.
  It enumerates each module's functions, so under mutmut it calls the
  generated `__mutmut_N` variants. Deselecting it drops all 7 of its
  parametrized cases (`PL-V10T`'s Hypothesis guard test), so a survivor in
  `core/supported_ranges.py` or a guarded constructor is not evidence of a
  gap.
- Then a second tier for each real-gap survivor: `mutmut apply` in a clean
  tree and
  `set -o pipefail; uv run pytest -q -x -n 2 -p no:cacheprovider tests/unit tests/integration tests/reference`.

**Pitfalls, each measured.**

- **Fork mode gives spurious kills.** mutmut's default `process_isolation` is
  `fork`. It runs the selected suite once in the parent, then forks per
  mutant, so every test module is imported once, unmutated. A test whose
  expected value was computed at import from mutated code can then kill a
  mutant that the same real defect would pass. This was reproduced for two
  `test_governing_equations` tests, whose oracle is the module-level
  `DELIVERED_FRACTION = fraction_from_percent(...)`: a 1% defect present
  before import passes them, and the same defect applied after import fails
  them. About 29 import-time call sites in 13 of the selected files reach
  mutated code. The forkserver settings above avoid this. Do not use the
  default warm-up `collect`, which imports test modules unmutated in the fork
  server and brings the problem back. On the mutants compared between the two
  modes, no fork-mode kill became a forkserver survivor, so the effect on
  this baseline looks small.
- **Forkserver mode is slower and times out.** It hit the two-hour limit
  part-way through, and about 49 fork-mode kills became forkserver timeouts
  (exit -24 or 255) from import overhead. Raise `timeout_constant` and re-run
  timeouts, or run the modules in chunks.
- **Some things are never mutated.** mutmut 3.8.0 does not mutate JSON data
  files, module-level constants, dataclass field defaults, `@property` or
  other decorated functions (except `@staticmethod` and `@classmethod`), type
  annotations, or calls to `len` and `isinstance`. Its number operator only
  adds 1, and it has no statement-deletion operator. So stored values and
  constants need stored-value perturbation instead.
- **"Killed" includes exceptions.** A mutant that only makes the code raise
  counts as killed, even though no assertion checked a value.
- **A full-suite stats pass is not practical.** Collecting per-test coverage
  over the whole suite took 81 minutes for 2024 tests in one process, and
  `test_doc_check`'s clean-repository test fails inside mutmut's `mutants/`
  copy. That is why integration and reference tests run only as the second
  tier.
- **Noise.** 11 of the 14 equivalent survivors in the matrix-exponential
  group are mutations of `strict=` on `zip` or `map`, where the lengths are
  equal by construction. A `# pragma: no mutate` on those lines would remove
  them from every future triage.

**The baseline (fork mode, `b9b3c812`).** 2619 mutants; 2439 tested and 180
not checked. Of those tested, 2147 were killed, 13 timed out and 279
survived: about 88% killed. Kill rate per module, as killed / (killed +
survived):

| Module | Killed / (killed + survived) | Rate |
| --- | --- | --- |
| `app/run_series.py` | 12 / 19 | 63% |
| `core/blood.py` | 52 / 71 | 73% |
| `core/agent_simulation_validation.py` | 78 / 103 | 76% |
| `core/tissue.py` | 67 / 86 | 78% |
| `core/checked_number.py` | 9 / 11 (18 not checked) | 82% |
| `core/simulation_step.py` | 28 / 33 | 85% |
| `core/concentration.py` | 34 / 40 (32 not checked) | 85% |
| `core/circuit.py` | 156 / 181 | 86% |
| `app/formatting.py` | 191 / 216 | 88% |
| `core/parameters.py` | 244 / 276 (76 not checked) | 88% |
| `core/matrix_exponential.py` | 217 / 243 | 89% |
| `core/supported_ranges.py` | 125 / 138 (19 not checked, 5 timeouts) | 91% |
| `core/uptake_system.py` | 200 / 220 | 91% |
| `core/run_definition.py` | 338 / 369 (6 timeouts) | 92% |
| `core/patient.py` | 101 / 110 | 92% |
| `core/exponential_approach.py` | 14 / 15 | 93% |
| `core/simulation.py` | 29 / 31 | 94% |
| `app/chart_time_base.py` | 63 / 67 (2 timeouts) | 94% |
| `core/governing_equations.py` | 141 / 148 | 95% |
| `core/alveolar.py` | 25 / 26 | 96% |
| `app/wash_in.py` | 21 / 21 | 100% |
| `core/validation.py` | 2 / 2 (35 not checked) | 100% |

`app/run_series.py` has the lowest rate but only 19 mutants; among the larger
modules `core/blood.py` is the weakest.

**Survivor triage.** Of the 279 survivors, 174 change only message text, 38
are equivalent, 13 are unreachable and 54 are real gaps. Of the 54, one is
safety (`record_change__mutmut_13`, filed as `PL-ZH1F`), one is medium
(`_propagator_for__mutmut_2`, filed as `PL-4H4T`), 41 are low and 11 have no
consequence. In the second tier, 36 of the 54 were run against the whole
suite: 28 survived all 5734 tests, and 8 were caught outside the 33 unit files
(5 by reference tests, 2 only by import-time constants, and 1 by a boundary
test added after the mutation run). The other 18 were not run within the time
box. The message-only class is `PL-79PK`. One low gap that is reachable today:
`fit_to_run__mutmut_13` widens the fitted time axis from 24 h to 48 h on the
final step of a run that reaches the 86,400 s limit, with a misleading caption
and no wrong value.

**Proposal: diff-scoped mutation.** Mutate only the functions a pull request
changes, and show the survivors at review, as Google does. Petrović et al.
report that developers first classified 85% of reported mutants as
unproductive, and that suppression rules raised the productive share to 89%
(Petrović G, Ivanković M, Fraser G, Just R. Practical mutation testing at
scale: a view from Google. IEEE Trans Softw Eng 48(10):3900-3912, 2022,
doi:10.1109/TSE.2021.3107634). A whole-tree run here costs hours and produces
mostly message noise. A diff-scoped run would cost minutes and ask about the
code under review.

**Where.** A recipe location to be decided, for example a section in
`docs/` or a commented `[tool.mutmut]` table; `pyproject.toml`'s dev group if
mutmut is ever added.

**Done when.** The recipe and this baseline are recorded where a session can
run them from, and a diff-scoped mutation run reports the survivors in the
functions a pull request changes.

**Related.** `PL-79PK` (the message-only survivors), `PL-ZH1F` and `PL-4H4T`
(the two real gaps that matter), `PL-0Z0F` (ready; perturbing
`supported_ranges` constants on a schedule, the constant-side counterpart).

**Generator check.** Not a member of any head. It proposes a measurement the
project never had, and no reader misread a recorded fact.

**Provenance.** A read-only test-effectiveness audit on 2026-10-17 found this.
The audit ran mutation testing with mutmut 3.8.0 over `core/` and four
presentation modules against the 33 simulator unit-test files (at
`b9b3c812`). It ran each real-gap survivor against the whole 5734-test
simulator suite (at `25ef454b`). It also used fault injection, stored-value
perturbation, oracle classification and regression-test replay, and an
adversarial second agent verified each finding. Its scratch files are not
durable, so the evidence is written out above.
