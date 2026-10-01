---
id: PL-HWNG
title: tests/unit/test_run_definition.py's _two_change_run sets sevoflurane's dial to 2.0%, where AgentUptakeSystem.for_agent already opens it at 1 MAC, so its first record_change may record nothing and every test built on it may be exercising one change rather than the two its name promises (reported while building PL-NJPB; the 2.0% matches the opening dial, but whether record_change skips an unchanged setting was not checked)
priority: P2
effort: S
status: ready
classes: test
touches: tests/unit/test_run_definition.py
added: 2026-10-01
payoff: the tests named for a two-change run exercise two changes, so a replay that loses a branch's second change is caught
verify: grep -q 'def test_the_two_change_run_carries_both_changes' tests/unit/test_run_definition.py
---

**Problem.** tests/unit/test_run_definition.py's _two_change_run sets sevoflurane's dial to 2.0%, where AgentUptakeSystem.for_agent already opens it at 1 MAC, so its first record_change may record nothing and every test built on it may be exercising one change rather than the two its name promises (reported while building PL-NJPB; the 2.0% matches the opening dial, but whether record_change skips an unchanged setting was not checked)

**Why it matters.** The run definition is what a branch replays, and every test built on `_two_change_run` claims a run carrying two setting changes. A replay that drops or misorders the second of two changes is the path those tests exist to hold, and they hold one.

**Done when.** `_two_change_run`'s first change moves the dial to a value other than the opening one, a test asserts the helper's run carries three segments (the opening and two changes), and the tests built on it still pass.

**Reproduced 2026-10-01.** Built with `uv run python`, `_two_change_run()` has two segments, opening at 0 s and 600 s: the 300 s change to 2.0% equals the dial sevoflurane opens at, and `record_change` drops a change equal to the settings in force, the first rule its docstring states.
