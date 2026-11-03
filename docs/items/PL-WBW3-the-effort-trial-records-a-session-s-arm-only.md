---
id: PL-WBW3
title: The effort trial records a session's arm only from its start-of-session line, so a session the owner moves to another level mid-session (session_01GnrHQs9QJ7TXfJF2dw2JpV, high to xhigh on 2026-11-03, PL-TN0G) is counted in the arm it left: give the model review a record of the move, or have it exclude such sessions
priority: P2
effort: S
status: ready
classes: defect
feature: effort-trial
touches: tools/effort_trial.py, tests/unit/test_effort_trial.py, .claude/hooks/docket-digest.sh, .claude/skills/model-review/SKILL.md
deferred-from: v0.7.0 - workflow tooling outside the schematic release
added: 2026-11-03
payoff: a session the owner moves to another effort level keeps that level and is analysed at it, not in the arm it left
verify: grep -q 'def test_a_level_set_mid_session_survives_compaction' tests/unit/test_effort_trial.py
---

**Problem.** The effort trial records a session's arm only from its start-of-session line, so a session the owner moves to another level mid-session (session_01GnrHQs9QJ7TXfJF2dw2JpV, high to xhigh on 2026-11-03, PL-TN0G) is counted in the arm it left: give the model review a record of the move, or have it exclude such sessions

**Found 2026-11-03, after compaction.** The session-start hook also runs on compaction, and it wrote the `high` cap back over the owner's `xhigh` change. The owner's move therefore lasts only until the next compaction, unless the session writes it again. A fix should leave a cap the owner set mid-session in place, or record the move so the hook can respect it.

**Why it matters.** The trial compares the two arms by how the work held up. A session the owner moved from `high` to `xhigh` did its work at `xhigh`, so counting it as `high` narrows the measured difference. The hook also writes the drawn cap back at each compaction, so the owner's move lasts only until then.

**Reproduced 2026-11-03, by reading.** `tools/effort_trial.py`'s docstring says the hook runs again when a session resumes or compacts, and that the hash gives the session the same arm each time.

**Done when.** The model review can tell which sessions changed level mid-session, and either uses the level they ran at or leaves them out. A compaction no longer writes the drawn cap over a level the owner set during the session.

**Generator check.** One-off pair with `PL-6LVZ`. Both misread the effort a session ran at, which the trial records only as the arm its hash drew.
