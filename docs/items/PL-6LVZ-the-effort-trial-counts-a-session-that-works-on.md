---
id: PL-6LVZ
title: The effort trial counts a session that works on a generator's cause in the arm its hash drew, though the owner's rule of 2026-11-02 runs that work at xhigh whatever the draw, so the analysis can treat a session forced to xhigh as randomized
priority: P2
effort: S
status: done
classes: defect
feature: effort-trial
milestone: v0.6.15
touches: tools/effort_trial.py, tests/unit/test_effort_trial.py, .claude/skills/model-review/SKILL.md, .claude/skills/docket/modes/triage.md, .claude/hooks/docket-digest.sh, .claude/hooks/hook_input.py, .claude/hooks/thread_hooks.py, docs/maintainer.md, docs/apparatus.md, docs/model-review.md
deferred-from: v0.7.0 - workflow tooling outside the schematic release
added: 2026-11-03
closed: 2026-11-03
pr: 1981
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

**Next steps, written 2026-11-03 by the "Finish the workflow lane" thread, which stopped for length before starting this pair.** Build `PL-6LVZ` and `PL-WBW3` together, on one branch, because both need one record of the level a session ran at and why it differs from the draw.

1. **Check first whether a Projects thread reads the cap at all.** `PL-CR81` found that a thread does not load `.claude/`, and only the setup script copies the hooks into `~/.claude/settings.json`. The hook then writes the cap into the repository's `.claude/settings.local.json`, which a thread may never read. The "Finish the workflow lane" thread printed "in the high arm", and `get_session` reported `effort_level: high`, but a thread started at `high` would report the same. If threads ignore the file, the hook should print "in neither arm" in a thread, which `CLAUDE_CODE_ENTRYPOINT=remote_projects` identifies, and the model review's step 6 already analyzes threads apart.
2. **Keep the record in the cap file.** `write_arm` also writes `effortTrial: {"session_id": ..., "drawn": ..., "level": ..., "reason": ...}` into `.claude/settings.local.json`.
3. **Add `python3 tools/effort_trial.py move --to xhigh --reason "<why>"`.** It writes the new cap, records the move with the session id (`CLAUDE_CODE_SESSION_ID`; check that it equals the hook's `session_id`), and prints "Effort trial: this session drew the high arm and was moved to xhigh, because <why>. The trial's review leaves it out." A session that starts work on a generator's cause runs it with reason `generator cause` (`PL-6LVZ`). The owner's own move runs it too (`PL-WBW3`).
4. **Make `session-start` respect a move.** When the record names the same session id and a moved level, rewrite that level and print the moved line instead of the drawn arm, so a compaction no longer undoes the owner's move. A different session id gets a fresh draw.
5. **Tell sessions when to run it.** `.claude/skills/docket/modes/triage.md` § "Generators, how they rank, and the pause they set" says a session working on a generator's cause runs the move first.
6. **Update the model review.** In `.claude/skills/model-review/SKILL.md` step 6, a session any of whose "Effort trial:" lines says it was moved is counted and left out of both arms. Report it at the level it ran at as the secondary result.
7. **Tests** named by the two `verify:` lines: `test_a_generator_cause_session_is_left_out_of_both_arms` and `test_a_level_set_mid_session_survives_compaction`.

**A Projects thread never read the cap, measured 2026-11-03.** The "Fix effort trial session counting" thread (session `session_01GnrHQthtvRuMSFHHtwUmnM`, Claude Code 2.1.317, `CLAUDE_CODE_ENTRYPOINT=remote_projects`) read its CLI diagnostics log. All five settings loads recorded `source_count: 2`, the user and launcher settings, as `PL-CR81` measured on 2026-10-26, when a hook written into `.claude/settings.local.json` never fired. The hook had still written a `high` cap into that file, and printed the `high` arm. So every thread's arm line since the trial began named a cap the thread never applied. A thread ran at the level the coordinator started it with, which `get_session` gives as `session_context.effort_level`. The hook's input `session_id` equals `CLAUDE_CODE_SESSION_ID`: the session's transcript file under `~/.claude/projects/` is named by it.

**Built 2026-11-03.** In a thread the hook now writes nothing and prints that the session is in neither arm. `python3 tools/effort_trial.py move --to LEVEL --reason WHY` writes the new cap and an `effortTrial` record of the session id, the drawn arm, the level and the reason, and prints a line saying the session was moved. The hook keeps a moved level for the same session id at a resume or a compaction. The model review's step 6 leaves moved sessions out of both arms, and `.claude/skills/docket/modes/triage.md` now records the owner's rule that work on a generator's cause runs at `xhigh` and says to run the move first.
