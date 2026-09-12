---
id: PL-BBDD
title: Nothing keeps docket.toml's gate_paths in step with the ruff.toml files in the tree, the job tools/workflow_paths_check.py already does for workflow_paths
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
touches: tools/workflow_paths_check.py, tests/unit/test_workflow_paths_check.py, docket.toml
added: 2026-09-08
closed: 2026-09-12
verify: uv run pytest tests/unit/test_workflow_paths_check.py && grep -q 'def test_a_ruff_toml_no_gate_path_covers_is_reported' tests/unit/test_workflow_paths_check.py
---

**Problem.** Nothing keeps docket.toml's gate_paths in step with the ruff.toml files in the tree, the job tools/workflow_paths_check.py already does for workflow_paths

**Where it comes from.** `PL-S2L4` (make `bin/docket delegable` stop offering
work `docs/worker.md` forbids) folds `docs/worker.md`'s "any `ruff.toml`" into
the configured gate list by naming `tools/ruff.toml` and
`subprojects/docket/ruff.toml` explicitly - `.claude/hooks/ruff.toml` is
already covered by the `.claude` entry. Naming them is a hand-maintained list
of files that appear as `tools/` and the subprojects grow, which is the shape
`docket.toml`'s own `workflow_paths` comment says drifted when it was
maintained that way (`PL-JBZK`): written with three entries, nine short a day
later, and silent in the direction that hurts.

**Why it matters.** A missed `ruff.toml` is silent in the same direction. The
`docket verify` check named "the checks themselves are unedited" reads
`gate_paths`, so an uncovered file lets a delegated diff relax the linter
config that keeps `tools/` and `subprojects/docket/` parseable by the bare
`python3` that runs them - and the audit reports ACCEPT.

**Approach.** `tools/workflow_paths_check.py` already does exactly this job
for `workflow_paths` - decides membership from the tree and fails `make check`
until the list agrees, printing the line to paste. The cheap version is a
second rule inside that script rather than a second script: every `ruff.toml`
in the tree must be covered by some `gate_paths` entry.

**Done when.** Adding a `ruff.toml` anywhere in the tree fails `make check`
until `docket.toml`'s `gate_paths` covers it.
