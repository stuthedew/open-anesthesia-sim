---
id: PL-S3TF
title: About 1,430 lines of guard Python live inside python3 -c strings in .claude/hooks/*.sh, where ruff, mypy and tools/fact_home_check.py never read them; direct-merge-guard.sh builds a second GitHub API client there, and three guards import json unused
priority: P2
effort: L
status: done
classes: refactor
feature: guard-review-2026-11
touches: .claude/hooks/floor_interpreter_guard.py, .claude/hooks/gate_status_guard.py, .claude/hooks/push_check_guard.py, .claude/hooks/direct_merge_guard.py, .claude/hooks/docket_branch_guard.py, .claude/hooks/guard.sh, .claude/hooks/hook_input.py, .claude/hooks/shell_split.py, docs/apparatus.md, Makefile, tools/fact_home_check.py, tests/unit/test_tools_portability.py, tests/unit/test_line_splits.py, tests/unit/test_docket_branch_guard.py
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
closed: 2026-11-04
pr: 1990
payoff: guard code is linted, type-checked and held to one source of truth like every other Python file, so defects like a second GitHub client stop accumulating unseen
verify: grep -q '^def decide' .claude/hooks/docket_branch_guard.py && ! grep -qF "python3 -c '" .claude/hooks/guard.sh
---

**Problem.** About 1,430 lines of guard Python live inside python3 -c strings in .claude/hooks/*.sh, where ruff, mypy and tools/fact_home_check.py never read them; direct-merge-guard.sh builds a second GitHub API client there, and three guards import json unused

**Why it matters.** Guard code inside a shell string is outside every check
the repository runs on Python: no lint, no type check, no one-source-of-truth
check. That is how `direct-merge-guard.sh` came to build a second GitHub API
client, and how three guards import `json` unused. It also forces the payload
through an environment variable, which `PL-B5K1` shows fails past 128 KiB.

<!-- absent: direct-merge-guard.sh -->

**Done when.** Each guard's Python lives in a module under `.claude/hooks/`
that ruff, mypy and `tools/fact_home_check.py` read, each `.sh` only starts
it, and `direct-merge-guard` uses the repository's one GitHub client.

**Generator check.** The shape behind `PL-B5K1` and part of `PL-9KSJ`, but not
itself a misread fact. It shares every guard file with the `PL-9KSJ` cluster,
so it is sequenced with that work.

**Progress, 2026-11-03 (#1990).** Four guards are done. The Python of
`floor-interpreter-guard.sh`, `push-check-guard.sh`, `gate-status-guard.sh` and
`direct-merge-guard.sh` now lives in `floor_interpreter_guard.py`,
`push_check_guard.py`, `gate_status_guard.py` and `direct_merge_guard.py`
beside them, and each `.sh` only starts its module. Ruff, mypy,
`tools/regex_check.py` and `tools/fact_home_check.py` read the modules, and
moving them in found constants named the same in two hooks and two
regular expressions with no stated reason. `direct_merge_guard.py` asks GitHub
through `tools/open_pull_requests.py`, the repository's one client. The
direct-merge guard still refuses any call mentioning a merge when Python
fails (`PL-NXRJ`). `pr-body-email-guard.sh` holds no Python of its own: it
starts `tools/pr_body_check.py --screen`.

<!-- absent: floor-interpreter-guard.sh -->
<!-- absent: push-check-guard.sh -->
<!-- absent: gate-status-guard.sh -->
<!-- absent: direct-merge-guard.sh -->
<!-- absent: pr-body-email-guard.sh -->

Two guards are left. `no-prune-guard.sh` is deleted by `PL-1ZZ0` (#1991),
which moves its check into git hooks. `docket-branch-guard.sh` is ported once
`PL-J22P` (#1989) merges, because that item rewrites the same Python to start
it once per call. The `verify:` line now names both.

<!-- absent: no-prune-guard.sh -->
<!-- absent: docket-branch-guard.sh -->
