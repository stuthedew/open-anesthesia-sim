---
id: PL-6LVZ
title: The effort trial counts a session that works on a generator's cause in the arm its hash drew, though the owner's rule of 2026-11-02 runs that work at xhigh whatever the draw, so the analysis can treat a session forced to xhigh as randomized
priority: P2
effort: S
status: ready
classes: defect
feature: effort-trial
touches: tools/effort_trial.py, tests/unit/test_effort_trial.py, .claude/skills/model-review/SKILL.md
deferred-from: v0.7.0 - workflow tooling outside the schematic release
added: 2026-11-03
payoff: the effort trial compares only sessions whose effort the draw set, so its result is not diluted by sessions the owner's rule forced to xhigh
verify: grep -q 'def test_a_generator_cause_session_is_left_out_of_both_arms' tests/unit/test_effort_trial.py
---

**Problem.** The project owner ruled on 2026-11-02, at 20:37 UTC: "Always run
proximal upstream generator issues (big picture stuff, figuring out why or
designing/implementing the cause fix) on extra high despite the current trial.
The down stream consequences of the issue can still be in trial." So a session
that works on a generator's cause runs at `xhigh` whatever arm it drew.

`tools/effort_trial.py` still draws an arm for such a session and prints it,
and its docstring says that printed line is the trial's record of the arm. The
model review in `PL-63CB` reads each session's arm from that line. Nothing
records which sessions the rule took out of the trial. A session drawn `high`
that ran at `xhigh` by the rule would be analysed as a `high` session, and one
drawn `xhigh` would be counted as randomized when the rule, not the draw, set
its effort.

Found on 2026-11-03 in the thread that built `PL-FYGJ` and `PL-CWRZ`, the
fourth and fifth fixes for `PL-H76S`. Its session-start hook printed the
`xhigh` arm. The coordinator asked that the session not be recorded as a trial
arm, and the repository had no record to correct.

**Why it matters.** The trial compares the two arms by how the work held up. A
session whose effort the rule fixed belongs to neither arm. Counted in the
`high` arm, it ran at `xhigh` and narrows the difference between the arms.
Counted in either arm, it adds work the draw did not assign.

**Done when.** The trial's analysis can tell which sessions worked on a
generator's cause, and leaves them out of both arms, or the owner decides they
stay in and the reason is recorded.

**Reproduced 2026-11-03, by reading.** `tools/effort_trial.py` draws an arm from the session id for every cloud session and never mentions generator work. This triage session's own hook printed the `xhigh` arm.

**Generator check.** One-off pair with `PL-WBW3`. Both misread the effort a session ran at, which the trial records only as the arm its hash drew. One record of the level a session ran at, and why it differs from the draw, would close both. No head states that fact.
