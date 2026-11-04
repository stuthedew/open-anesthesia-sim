---
id: PL-J22P
title: docket-branch-guard.sh starts Python twice before it checks its markers, about 95 ms on every Edit and Bash call after its questions are spent
priority: P3
effort: S
status: done
classes: perf
feature: guard-review-2026-11
touches: .claude/hooks/docket-branch-guard.sh, tests/unit/test_docket_branch_guard.py
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
closed: 2026-11-03
pr: 1989
payoff: every Edit and Bash call after a session's first edit is about 50 ms cheaper
verify: grep -q 'def test_spent_markers_start_python_once' tests/unit/test_docket_branch_guard.py
---

**Problem.** docket-branch-guard.sh starts Python twice before it checks its markers, about 95 ms on every Edit and Bash call after its questions are spent

**Why it matters.** `docket-branch-guard.sh` starts Python once to find the
checkout and once to read the session id, before it checks whether this
session's two markers already exist. After the first edit both exist, so every
later Edit and Bash call pays about 95 ms for nothing.

**Done when.** A session whose markers both exist pays at most one Python
start in this hook, and a test that times or counts the starts with both
markers present pins it.

**Generator check.** A one-off cost in one hook.
