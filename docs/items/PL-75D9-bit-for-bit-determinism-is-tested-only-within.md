---
id: PL-75D9
title: Bit-for-bit determinism is tested only within one interpreter process, and CI never randomizes test order, so hash-seed-dependent iteration or a new order dependence between tests would pass every gate
status: untriaged
feature: test-effectiveness-measurement
added: 2026-10-17
---

**Problem.** Bit-for-bit determinism is tested only within one interpreter process, and CI never randomizes test order, so hash-seed-dependent iteration or a new order dependence between tests would pass every gate

**Severity: low.** No present defect: both properties hold today, and only
this audit's one-off runs show it. Audit findings CMP-7 and REL-DET-1
(confirmed) and REL-ORDER-1 (verifier: "partly"; the corrected claim is used
below).

**Determinism across processes.** Every determinism test compares two runs
inside one interpreter: `test_identical_runs_produce_identical_snapshots_and_history`
in `tests/integration/test_sevo_controller.py`,
`test_start_advance_pause_sequence_is_deterministic` in
`tests/integration/test_controller.py`,
`test_the_canonical_path_answers_bit_identically_twice` in
`tests/unit/test_run_definition.py` and
`test_two_evaluations_of_one_instant_are_bit_identical` in
`tests/reference/test_canonical_evaluation.py`. `PYTHONHASHSEED` appears
nowhere under `tests/`, in `conftest.py`, in `pyproject.toml` or in the CI
workflows. The only simulator tests that start subprocesses are
import-boundary probes. `PINNED_REFERENCE_STATES` is compared with
`pytest.approx(rel=1e-9, abs=1e-15)`, not bit for bit. `docs/MODEL.md` claims
element-wise identical runs within one build, and excludes other platforms.

A probe across processes held. Three agents x 6000 steps under
`PYTHONHASHSEED` 0, 12345 and random gave one SHA-256 over
`repr(snapshot) + repr(run_segments)`. The verifier reproduced it
independently, with 3000 steps at 0.1 s and a fresh-gas change at step 1000,
under seeds 0, 12345 and 999. `core/` iterates no sets in arithmetic; its only
sets are frozensets used for membership. `tools/import_boundary_check.py`
refuses `time`, `random` and `uuid` imports in `core/`, but nothing checks for
iteration in hash order.

**Test order.** 5519 of 5519 tests passed with pytest-randomly at seeds 12345
and 271828 (a per-test comparison of the two junit reports found no change).
They also passed in reverse order over the 55 simulator files, and in a
single process forward, shuffled and reversed. So there is no order
dependence today. CI (`.github/workflows/quality.yml` and the `Makefile`,
`-n 2*cpu --dist worksteal`) never randomizes the order. Worksteal gives each
worker a contiguous slice, and the `trylast` hook in `tests/conftest.py` calls
`deal()` to move costly tests to the head of each slice. So a test that relies
on an earlier test's side effect can still surface at a slice boundary. But a
test that fails only when it runs before another is never exercised.
pytest-randomly is in neither `pyproject.toml` nor `uv.lock`. In Python, order
dependence caused 59% of 7571 flaky tests in one large study (Gruber et al.,
ICST 2021, doi:10.1109/ICST49551.2021.00026).

**Why it matters.** A future `for name in some_set:` accumulation in `core/`,
or ordering by `id()`, would pass the whole suite while two learners' runs of
the same case differed in the last bits. A new order dependence would surface
as an unrelated pull request going red, or as a spurious kill or survivor in
a mutation run, which uses a fixed order.

**Where.** A new integration test for determinism; `pyproject.toml`,
`.github/workflows/` and `Makefile` for a randomized-order job.

**Recommended work.**

1. Add one test, about 1-2 s, that runs a fixed 10-minute case with several
   changes in two subprocesses with different `PYTHONHASHSEED` values, and
   once in process. Compare `float.hex` of the six fractions and both
   accumulators, or digests of `repr(snapshot)` and `repr(run_segments)`. Do
   not pin a golden digest, because `docs/MODEL.md` excludes other platforms
   and macOS's libm would differ.
2. Add a scheduled job with a randomized test order: pytest-randomly in the
   dev group, `-p no:randomly` in pyproject's `addopts` so every other run
   stays deterministic, and `-p randomly --randomly-seed=$(date +%Y%m%d)` in
   a weekly job (`drift.yml` already runs on a schedule). A red run names its
   seed, so it reproduces exactly. Putting the opt-out in `addopts` matters:
   opt-outs on two command lines alone would shuffle every other invocation,
   including sessions' own `uv run pytest` runs.

The first is simulator test work. The second is a CI job.

**Decision.** The project owner approved both (project owner, 2026-10-17,
ratified, over leaving determinism across processes and independence of test
order to one-off audits). The capture said the job fell under `CLAUDE.md`'s
pause on new workflow mechanisms. That was wrong, because no workflow-lane
head carried `generator: live` that day (`PL-3KMD`).

**Done when.** A test compares a run across processes with different hash
seeds, and a scheduled job runs the suite in a randomized order.

**Provenance.** A read-only test-effectiveness audit on 2026-10-17 found this.
The audit ran mutation testing with mutmut 3.8.0 over `core/` and four
presentation modules against the 33 simulator unit-test files (at
`b9b3c812`). It ran each real-gap survivor against the whole 5734-test
simulator suite (at `25ef454b`). It also used fault injection, stored-value
perturbation, oracle classification and regression-test replay, and an
adversarial second agent verified each finding. Its scratch files are not
durable, so the evidence is written out above. Symbols re-checked against
`9ea87a3c`.
