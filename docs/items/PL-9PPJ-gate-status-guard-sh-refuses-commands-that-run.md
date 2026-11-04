---
id: PL-9PPJ
title: gate-status-guard.sh refuses commands that run no gate: timing tools/doc_check.py with output sent to /dev/null, ruff --version | head, pytest --collect-only | tail; and it refuses make check && echo PASS || echo FAIL while admitting make check || echo failed: $?, though both print the verdict
priority: P2
effort: S
status: done
classes: defect
feature: guard-review-2026-11
milestone: v0.6.15
touches: .claude/hooks/gate-status-guard.sh, tests/unit/test_gate_status_guard.py, .claude/skills/docket/modes/coordinator.md, docs/maintainer.md
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
closed: 2026-11-03
pr: 1989
payoff: a session checking a tool's version or listing tests through a pipe is no longer refused and sent to retry
verify: grep -q 'def test_a_version_run_piped_to_head_is_admitted' tests/unit/test_gate_status_guard.py
reenters: PL-61FT
---

**Problem.** gate-status-guard.sh refuses commands that run no gate: timing tools/doc_check.py with output sent to /dev/null, ruff --version | head, pytest --collect-only | tail; and it refuses make check && echo PASS || echo FAIL while admitting make check || echo failed: $?, though both print the verdict

**Reproduced 2026-11-03.** `gate-status-guard.sh` refused `ruff --version |
head -1`, `uv run pytest --collect-only -q | tail -3` and `make check && echo
PASS || echo FAIL`, and admitted `make check || echo failed: $?`. None of the
three refused commands loses a gate's verdict: the first two run no gate, and
the third prints its verdict as the last two do.

**Why it matters.** A false refusal costs a session a retry and teaches it to
route around the guard. One caution for the fix:
`.claude/skills/docket/modes/coordinator.md` § "What every brief tells its
thread" uses the refusal of `uv run pytest --version | head -1` to tell whether
a thread has the hooks, so that probe must change in the same commit.

**Done when.** A version or collect-only run piped to `head` or `tail` is
admitted, `&& echo PASS || echo FAIL` is admitted as `|| echo failed: $?` is,
the coordinator's probe uses a command the guard still refuses, and a test
pins each.

**Generator check.** A re-entry of `PL-61FT` (what a shell command does when
run), met in ordinary work: this thread was refused `uv run pytest --version |
head -1` on 2026-11-03. Fixed at its own rank.
