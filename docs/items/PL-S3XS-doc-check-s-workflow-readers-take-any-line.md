---
id: PL-S3XS
title: doc_check's workflow readers take any line opening with run: for a step's key and whatever follows on: on its line for the whole value, so a line inside a block scalar reads as a step and a workflow whose on: carries a comment or an anchor reads as triggered by nothing, and gate parity passes; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by PL-848V's thread, 2026-10-05
added: 2026-10-04
payoff: a workflow's run steps are read where YAML puts them and its on: whatever comment or anchor it carries, so gate parity and the coverage gate compare what CI actually runs
verify: grep -q 'workflow commands, a run key inside another block scalar is no step' tests/unit/test_doc_check.py && grep -q 'pull request trigger, an on: key carrying a comment' tests/unit/test_doc_check.py
recurrences: 2026-10-04 PL-PPNV withdrawn 2026-10-04 PL-R417, 2026-10-04 PL-T1X0 withdrawn 2026-10-04 PL-R417
---

**Problem.** doc_check's workflow readers take any line opening with run: for a step's key and whatever follows on: on its line for the whole value, so a line inside a block scalar reads as a step and a workflow whose on: carries a comment or an anchor reads as triggered by nothing, and gate parity passes; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

YAML 1.2.2 § 8.1 (a block scalar's lines are content), § 7.4 (a flow mapping spans lines), § 6.6 and § 6.9 (a comment and an anchor after a key).

- `RUN_STEP_RE` in `workflow_commands`: a github-script step whose `script: |` holds "run: python3 tools/not_a_step.py" yields that as a step; `- {name: x,` over `   run: python3 tools/real_step.py}` yields the command with its `}`; and `defaults:` / `run:` / `shell: bash` is declined as a step, which stops `check_coverage_gate` and `check_gate_parity` comparing.
- `ON_BLOCK_RE` in `_gates_pull_requests`: "on:  # what starts this workflow" over "  pull_request:", and `on: &triggers`, read as gating no pull request. End to end, with `make check` running `tools/a.py` and `tools/b.py` and the pull-request workflow only `a.py`, a bare `on:` raises the parity error and the commented one raises nothing.

Latent: all 44 run steps in the six workflows match PyYAML 6.0.3, and every `on:` is bare.

**Why it matters.** `check_gate_parity` and `check_coverage_gate` compare what `make check` runs with what the merge gate runs, reading a workflow's steps through `workflow_commands` and whether it gates a pull request through `_gates_pull_requests`. A `run:` line inside another key's block scalar reads as a step the workflow never runs, a flow-mapping step's command keeps its closing brace, and a `defaults:` `run:` block is declined as a step, which stops both comparisons; a workflow whose `on:` carries a comment or an anchor reads as gating no pull request, so the scripts only it runs read as missing from the merge gate. Each is ordinary YAML a workflow edit can introduce.

**Reproduced 2026-10-05, at triage.** On Python 3.11.15, against `main` at `f84e31f9`: `workflow_commands` yielded `python3 tools/not_a_step.py` from a github-script step's `script: |` body and `python3 tools/real_step.py}` from `- {name: x,` over `   run: python3 tools/real_step.py}`, and declined a top-level `defaults:` over `  run:` over `    shell: bash` as a step opening on the line after its key; `_gates_pull_requests` read `on:  # what starts this workflow` over `  pull_request:`, and `on: &triggers` over `  pull_request:`, as gating no pull request, where the bare `on:` over `  pull_request:` read as gating.

**Done when.** `workflow_commands` reads a `run:` only where YAML puts a step's key, under a job's `steps:`, so a `run:` line inside another key's block scalar or under `defaults:` is no step, and a step written as a flow mapping is read whole or refused by name; `CONTINUED_STATEMENTS` in `tests/unit/test_doc_check.py` gains `workflow commands, a run key inside another block scalar is no step`. That is `PL-R417`'s YAML slice's, so this item stays open until that slice.

**The `on:` half is done (`#1366`, 2026-10-05).** `_gates_pull_requests` reads an `on:` carrying a comment or an anchor through `required_checks_check.triggers`, the one reader of a workflow's triggers that `PL-848V` built, and `CONTINUED_STATEMENTS` gained `pull request trigger, an on: key carrying a comment`.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names. Its `on:` half is also a member of `PL-848V`, the head for which events a workflow's `on:` names.
