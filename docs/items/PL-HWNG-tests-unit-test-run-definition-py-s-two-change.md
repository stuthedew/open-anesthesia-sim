---
id: PL-HWNG
title: tests/unit/test_run_definition.py's _two_change_run sets sevoflurane's dial to 2.0%, where AgentUptakeSystem.for_agent already opens it at 1 MAC, so its first record_change may record nothing and every test built on it may be exercising one change rather than the two its name promises (reported while building PL-NJPB; the 2.0% matches the opening dial, but whether record_change skips an unchanged setting was not checked)
priority: P2
effort: S
status: ready
classes: test
feature: two-change-run-has-two-changes
touches: tests/unit/test_run_definition.py
added: 2026-10-01
payoff: the tests named for a two-change run exercise two changes, so a replay that loses a branch's second change is caught
verify: grep -q 'def test_the_two_change_run_carries_both_changes' tests/unit/test_run_definition.py
recurrences: 2026-10-04 PL-KZXJ
---

**Problem.** tests/unit/test_run_definition.py's _two_change_run sets sevoflurane's dial to 2.0%, where AgentUptakeSystem.for_agent already opens it at 1 MAC, so its first record_change may record nothing and every test built on it may be exercising one change rather than the two its name promises (reported while building PL-NJPB; the 2.0% matches the opening dial, but whether record_change skips an unchanged setting was not checked)

**Why it matters.** The run definition is what a branch replays, and every test built on `_two_change_run` claims a run carrying two setting changes. A replay that drops or misorders the second of two changes is the path those tests exist to hold, and they hold one.

**Done when.** `_two_change_run`'s first change moves the dial to a value other than the opening one, `test_the_two_change_run_carries_both_changes` asserts the helper's run carries three segments (the opening and two changes), and the tests built on it still pass. The run `FORK_OFF_KEYFRAME_DIVERGENCE_CEILING` was measured on changes with it, so the ceiling is re-measured on the new run - the divergence at each probe recorded in the commit, and the ceiling kept or moved to bound it - and its comment and the helper's docstring describe the run they now stand on, rather than being relabelled.

**Reproduced 2026-10-01.** Built with `uv run python`, `_two_change_run()` has two segments, opening at 0 s and 600 s: the 300 s change to 2.0% equals the dial sevoflurane opens at, and `record_change` drops a change equal to the settings in force, the first rule its docstring states.

**Answered 2026-10-05, from `PL-KZXJ`.** `record_change` does skip an unchanged
setting: its docstring says settings equal to the ones in force "describe no
change the model would integrate differently" and drops them, and `PL-CNCF`'s
first fixture, which copied this helper's 2.0% dial, recorded no stretch at its
change and failed a count of three stretches until the dial moved to 3.0%
(found 2026-10-04 while building `PL-CNCF`). `AgentUptakeSystem.for_agent("sevoflurane")`
opens at a 2.0% dial, 4.0 L/min fresh gas, 4.0 L/min alveolar ventilation and
5.0 L/min cardiac output, so `_two_change_run` carries one change, the fresh
gas flow at 600 s. Confirmed 2026-10-05 with one `uv run python -c` importing
the helper from `tests/unit/test_run_definition.py`: `opening dial 2.0 % |
segments 2 | opening instants [0.0, 600.0]`. Two things pinned on that run
describe one that never existed: the helper's docstring ("carrying two setting
changes") and the comment over `FORK_OFF_KEYFRAME_DIVERGENCE_CEILING` ("on the
two-change sevoflurane run below"). One test is built on the helper,
`test_opening_a_branch_off_a_keyframe_does_not_reproduce_the_run`, and moving
the dial changes the run its ceiling was measured on, so the fix re-measures the
ceiling rather than relabelling it; the Done-when above now says so.
