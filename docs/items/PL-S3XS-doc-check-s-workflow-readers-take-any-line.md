---
id: PL-S3XS
title: doc_check's workflow readers take any line opening with run: for a step's key and whatever follows on: on its line for the whole value, so a line inside a block scalar reads as a step and a workflow whose on: carries a comment or an anchor reads as triggered by nothing, and gate parity passes; latent
status: untriaged
feature: one-answer
touches: tools/doc_check.py, tests/unit
added: 2026-10-04
recurrences: 2026-10-04 PL-PPNV withdrawn 2026-10-04 PL-R417, 2026-10-04 PL-T1X0 withdrawn 2026-10-04 PL-R417
---

**Problem.** doc_check's workflow readers take any line opening with run: for a step's key and whatever follows on: on its line for the whole value, so a line inside a block scalar reads as a step and a workflow whose on: carries a comment or an anchor reads as triggered by nothing, and gate parity passes; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

YAML 1.2.2 § 8.1 (a block scalar's lines are content), § 7.4 (a flow mapping spans lines), § 6.6 and § 6.9 (a comment and an anchor after a key).

- `RUN_STEP_RE` in `workflow_commands`: a github-script step whose `script: |` holds "run: python3 tools/not_a_step.py" yields that as a step; `- {name: x,` over `   run: python3 tools/real_step.py}` yields the command with its `}`; and `defaults:` / `run:` / `shell: bash` is declined as a step, which stops `check_coverage_gate` and `check_gate_parity` comparing.
- `ON_BLOCK_RE` in `_gates_pull_requests`: "on:  # what starts this workflow" over "  pull_request:", and `on: &triggers`, read as gating no pull request. End to end, with `make check` running `tools/a.py` and `tools/b.py` and the pull-request workflow only `a.py`, a bare `on:` raises the parity error and the commented one raises nothing.

Latent: all 44 run steps in the six workflows match PyYAML 6.0.3, and every `on:` is bare.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names. Its `on:` half is also a member of `PL-848V`, the head for which events a workflow's `on:` names.
