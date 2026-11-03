---
id: PL-VDK9
title: gate-status-guard.sh's remedy 'make check && tail -45 /tmp/gate.log' has no redirect, so copied as written it prints the whole run and then the tail of an older log; its test pins the text, not what it does
priority: P2
effort: S
status: done
classes: defect
feature: guard-review-2026-11
touches: .claude/hooks/gate-status-guard.sh, tests/unit/test_gate_status_guard.py
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
closed: 2026-11-03
pr: 1989
payoff: the remedy a refused session copies prints the tail of this run, not the whole run followed by an older log
verify: grep -q 'def test_each_offered_remedy_redirects_into_its_log' tests/unit/test_gate_status_guard.py
---

**Problem.** gate-status-guard.sh's remedy 'make check && tail -45 /tmp/gate.log' has no redirect, so copied as written it prints the whole run and then the tail of an older log; its test pins the text, not what it does

**Reproduced 2026-11-03.** The refusal this thread met lists `uv run pytest
--version && tail -45 /tmp/gate.log` as an accepted spelling. Copied as
written it prints the whole run and then the tail of whatever older log
`/tmp/gate.log` holds.

**Why it matters.** The refusal is read at the moment a session wants the
remedy, and a remedy that does not work wastes the retry and the context it
was meant to save.

**Done when.** Every remedy the refusal offers redirects the run into the log
it then reads, and a test runs each offered spelling through the guard and
checks it is admitted and carries the redirect.

**Generator check.** A one-off in the refusal's text.
