# Review verification harness

Executable evidence for the independent architecture review of the v0.2.0
baseline (commit `3251ebf`). Every numeric claim the review makes is
produced by a script here, so a later reader — human or agent — can re-run
the claim instead of trusting the write-up.

Seven of the nine checks have since been fixed and now report `FIXED`:
`P1-2` (PL-015), `P1-3` (PL-017), and `P1-5` (PL-016) in v0.2.1; `P1-1`
(both of its checks, PL-018), `P1-6` (PL-022), and `P1-4` (PL-021) in
v0.2.2. Their rows below describe the reviewed v0.2.0 behaviour, which is what
the checks still probe for. `verify_findings.py` therefore exits `1` on a current
tree, as designed.

These scripts are **not** part of the test suite and **not** a fix for
anything they report. They are read-only diagnostics that live outside
`src/` and `tests/` deliberately.

## Running

```bash
uv run python tools/review-verification/verify_physics.py    # ~20 s
uv run python tools/review-verification/verify_findings.py   # ~15 s
```

Both exit `0` when the working tree still behaves exactly as reviewed, and
`1` when something changed. Exit `1` is the useful signal, not a failure:
it means a finding was fixed (or a physics claim regressed) and the review
write-up is now stale for that item.

## What each check reports

| State | Meaning |
| --- | --- |
| `CONFIRMED` | A correctness claim from the review still holds. |
| `REGRESSED` | A correctness claim no longer holds — the implementation changed for the worse. |
| `REPRODUCED` | A reported defect is still present. |
| `FIXED` | A reported defect is gone. Update the review text. |

## `verify_physics.py`

Re-derives the governing equations of `docs/MODEL.md` from the loaded
parameter files and integrates them with a from-scratch RK4. It imports no
solver from `core/` — only the parameter loaders — so agreement between the
two is genuine verification rather than a tautology.

| Check | Claim |
| --- | --- |
| `P2-2` | The shipped operator split reproduces the documented equations (worst max-abs error ~2e-5 at `Δt = 0.1 s`, 5% delivered). |
| `P2-3` | The splitting error is genuinely first order — halving `Δt` halves the error, ratio 2.00 at every refinement. |
| `ARCH` | The system is linear and time-invariant within a step, so a single matrix exponential is *exact* (~1e-15) where the pairwise split is not (~1e-5). |

The `ARCH` check is the evidence behind the review's central architectural
recommendation. It builds a scaling-and-squaring matrix exponential in pure
Python, with no dependencies, and steps the same six-state system with it.

**This is not the fix for `P2-2`.** The actual remedy is to promote this
RK4 oracle into `tests/reference/` with pinned vectors, so the coupled
model is checked against an independent solution on every CI run. This
script only demonstrates that such a test would pass today.

## `verify_findings.py`

Reproduces each defect the review reported, using only public API plus one
documented private import.

| Check | Claim |
| --- | --- |
| `P1-1` | A core guard raises a bare `ValueError` outside the project's own `AnesthesiaSimulationError` hierarchy, and `SimulationView._run_simulation_timer` has no exception handling — so the asyncio task dies while the UI still reads "Running". |
| `P1-2` | `SimulationController.set_delivered_concentration` ignores the agent's vaporizer maximum (50% isoflurane on a 5% device is accepted and simulated). |
| `P1-3` | `reference_adult.json`'s cited `default_cardiac_output_l_min` / `default_alveolar_ventilation_l_min` never reach the running app; the controller's hardcoded literals win. |
| `P1-4` | The Pydantic schemas silently ignore unknown keys — a misspelled `blood_gas_partitition_coefficient` is dropped and the old value used. No model sets `extra="forbid"`. |
| `P1-5` | `_AgentPayload`'s MAC cross-check reads `info.data`, so it depends on field declaration order and fails *open*: reorder two fields and 40% MAC on a 5% vaporizer validates clean. |
| `P1-6` | `AlveolarCompartment.advance_ventilation` has no call site anywhere in the shipped package, and does not conserve agent — it credits the alveoli with no matching circuit debit. |
| `P2-1` | Mass balance passes (residual ~2e-15 L) while the dynamics are visibly wrong (0.157 percentage points off at `Δt = 10 s`), because every internal transfer is applied as an equal-and-opposite pair. It cannot detect a wrong rate. |
| `P2-4` | The 1.0 L venous pool — the compartment with the least provenance in `docs/MODEL.md` — shifts displayed mixed-venous by up to 55% during the first minute of wash-in. |

### Notes on how these are checked

- `P1-3` monkeypatches `respiratory_system.load_reference_adult_parameters`
  with a `dataclasses.replace` copy carrying different defaults, then
  restores it in a `finally` block. Nothing on disk is touched.
- `P1-5` pulls the shipped guard function off `_AgentPayload` and
  re-registers it — the way the shipped model registers it — on minimal
  models declaring the two fields in each order, rather than mutating
  `_AgentPayload` itself. The check is safe to run and probes the real
  guard, not a look-alike.
- `P1-2` reports `FIXED` when the request is rejected outright, and also
  if it were clamped: what it tests is that the run does not continue at a
  dial position the vaporizer does not have.
- Both scripts run at 5% delivered, the highest concentration all three
  shipped vaporizers can produce. 8%, the reviewed operating point, is now
  rejected for isoflurane rather than simulated.
- `P1-4` adds its misspelled key *alongside* the correctly spelled one, so
  what it probes is an unknown extra key rather than a missing required one.
  A misspelling that removes a required key is already rejected as a missing
  field; the hole is the key an author adds believing it takes effect. It
  also probes a nested key, so a schema strict only at the top level still
  reports `REPRODUCED`. Both probes catch `AnesthesiaSimulationError`
  rather than `ValueError`: the loaders re-raise Pydantic's error as
  `SimulationConfigurationError`, which is deliberately outside the
  `ValueError` hierarchy.
- `P1-6` first tests whether `AlveolarCompartment.advance_ventilation`
  still exists. PL-022 deleted it, so the check reports `FIXED` on that
  branch and never calls it — calling a deleted method would raise instead
  of reporting. If the method ever comes back, the original probe runs
  again: it scans every shipped module's source for a
  `.advance_ventilation(` call site and checks whether one step credits the
  alveoli with no matching debit. On that path a wired-up call site also
  flips the check to `FIXED` — the wrong outcome for the right reason — so
  read the detail line rather than the state alone.

## Findings not covered here

The review reports 21 findings. The 8 above are the ones with a crisp
programmatic reproduction. The rest are design, presentation, and
documentation judgements that a script cannot adjudicate — false precision
in displayed values, an agent-dependent chart axis, stale claims across
`README.md` / `ROADMAP.md` / `WORKING_NOTES.md` / `ARCHITECTURE.md`, and
the tooling gaps (`mypy` skipping `tests/`, a narrow Ruff rule set,
unenforced coverage). Those need a reader, not a runner.
