---
id: PL-KZXJ
title: tests/unit/test_run_definition.py's _two_change_run says it carries two setting changes, but its first - a 2.0% sevoflurane dial at 300 s - is the agent's default, so record_change drops it and the run carries one; the fork-divergence ceiling and the comment pinned on that run describe a two-change run that never existed
status: untriaged
feature: two-change-run-has-two-changes
added: 2026-10-04
---

**Problem.** tests/unit/test_run_definition.py's _two_change_run says it carries two setting changes, but its first - a 2.0% sevoflurane dial at 300 s - is the agent's default, so record_change drops it and the run carries one; the fork-divergence ceiling and the comment pinned on that run describe a two-change run that never existed

**The same problem as `PL-HWNG`, with its open question answered** (found
2026-10-04 while building `PL-CNCF`). `PL-HWNG` left unchecked whether
`record_change` skips an unchanged setting. It does: its docstring says
settings equal to the ones in force "describe no change the model would
integrate differently" and are dropped, and `PL-CNCF`'s first test fixture,
which copied this helper's 2.0% dial, recorded no stretch at its change and
failed a count of three stretches until the dial was moved to 3.0%.
`AgentUptakeSystem.for_agent("sevoflurane")` opens at a 2.0% dial, 4.0 L/min
fresh gas, 4.0 L/min alveolar ventilation and 5.0 L/min cardiac output.

So `_two_change_run` carries one change, the fresh gas flow at 600 s, and two
things pinned on it describe a run that never existed: its own docstring, and
the comment over `FORK_OFF_KEYFRAME_DIVERGENCE_CEILING` ("on the two-change
sevoflurane run below"). Moving the dial off the default changes the run that
ceiling was measured on, so the fix re-measures it rather than only re-labelling
it. Fold into `PL-HWNG` at triage.
