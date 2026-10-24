---
id: PL-8MZ9
title: The effort trial has put no session in either arm: the cloud environment runs its setup script once and reuses a snapshot, and the snapshot was taken before the trial started
priority: P2
effort: M
status: done
classes: defect, infra
milestone: v0.6.2
touches: docs/items/PL-8MZ9-the-effort-trial-has-put-no-session-in-either.md, tools/effort_trial.py, tests/unit/test_effort_trial.py, .claude/hooks/docket-digest.sh, docs/maintainer.md, docs/apparatus.md, docs/items/PL-63CB-add-a-model-review-skill-that-on-a-cadence-and.md
added: 2026-10-24
closed: 2026-10-24
pr: 1743
payoff: the effort trial assigns each cloud session its own arm, so its result can say whether high effort causes real problems, and sessions stop opening with a line the owner cannot decode
verify: grep -qE '^\*\*Probe result' docs/items/PL-8MZ9-the-effort-trial-has-put-no-session-in-either.md && grep -q 'session_id' tools/effort_trial.py
---

**Problem.** The effort trial has put no session in either arm: the cloud environment runs its setup script once and reuses a snapshot, and the snapshot was taken before the trial started

**Why it matters.** The trial exists to test, by random assignment, whether `high` effort causes real problems that `xhigh` avoids (`PL-HYRM`, `PL-63CB` § "Effort monitoring"). As it stands it assigns nothing. Every cloud session since the trial started opens with a line like "this session's effort trial arm is 'none' with no `maxEffortLevel` set". The session-start digest tells each session to report its arm in its first reply. In the "none" case, `digest_line` in `tools/effort_trial.py` gives the session a settings key and a log path, not what they mean. The owner asked what these reports were about (2026-10-24, with a screenshot of one).

**Measured in session `session_01NER65c1ZjauPPqsWb3HELp`, 2026-10-24.**

- `/tmp/effort-trial.log` holds one line, `2026-10-23T23:55:52+00:00 high not-written: before the trial start`. That is 6:55 pm CDT on Friday 2026-10-23, four hours before the trial began at 11 pm CDT. The session itself was created at 2:55 pm CDT on 2026-10-24.
- `/tmp/env-manager.log` records `"session_mode":"resume-cached"` and "Repositories updated successfully in resume-cached mode". `/tmp` also holds another session's environment-manager lock from 6:55 pm CDT on 2026-10-23. So this session started from a snapshot of an earlier session's container, and the setup script did not run for it.
- No `.claude/settings.local.json` exists, so no cap applies. The app started Claude Code with `--effort xhigh`, and `CLAUDE_EFFORT` reads `xhigh`.
- The session's own transcript records `"effort":"xhigh"` and `"perTurnEffort":"xhigh"` on each turn. That is a per-turn record of the level actually run. It is more direct than `CLAUDE_EFFORT`, and the model review can use it.

**What the docs say.** "The setup script runs the first time you start a session in an environment. When setup completes within roughly five minutes, Anthropic snapshots the filesystem and reuses that snapshot as the starting point for later sessions. New sessions … skip the setup script step." The script runs again only "when you change the environment's setup script or allowed network hosts, and when the cache reaches its expiry after roughly seven days" (Claude Code docs, *Cloud environments*, section "Environment caching", https://code.claude.com/docs/en/cloud-environments.md, read 2026-10-24). `PL-HYRM` (the item that built the trial's assignment) assumed the script runs "each time a container is built fresh", which these docs contradict.

**What follows.**

1. **No session has been in the trial so far.** The snapshot carries the before-the-start result, so every session since 11 pm CDT on 2026-10-23 has run at whatever level the app's picker sent. That is inferred for sessions other than the one above, from the shared snapshot. The screenshot the owner sent shows a second session reporting "none".
2. **Once the snapshot is rebuilt, every session shares one arm for about a week.** The rebuild happens at the roughly seven-day expiry, about 6:55 pm CDT on Friday 2026-10-30, or sooner if the setup script or the allowed hosts change. The script then draws once. Its `.claude/settings.local.json` is ignored by git and so survives the repository update in each later session. A whole week then runs at `high`, or, one time in four, at `xhigh`. That is one random draw per week, not per session, so the trial's comparison would be confounded with whatever work each week held.
3. **The picker is not staying at `xhigh`.** Of the 10 sessions opened from the app since the trial started, 4 asked for `high` (`session_context.effort_level` from `list_sessions`, read 2026-10-24). A cap cannot raise a level, so a session in the `xhigh` arm whose picker sent `high` runs at `high`. `docs/maintainer.md` says the app keeps its last level. These 10 sessions say that either the app does not, or the picker was changed.

**Recommended route (session's recommendation, for the owner's decision).** Move the draw from the setup script to the `SessionStart` hook, which runs in every session, cached or not.

- The hook writes the arm as `maxEffortLevel` and `effortLevel` into `.claude/settings.local.json`, as the setup script does now.
- Claude Code "watches your settings files and reloads them when they change", and reads only some keys once at start, `effortLevel` among them (*Settings*, section "When edits take effect", https://code.claude.com/docs/en/settings.md, read 2026-10-24). `maxEffortLevel` is not in that list, and "Claude Code applies the cap itself before each request" (*Settings reference*, `maxEffortLevel`, https://code.claude.com/docs/en/settings-reference.md, read 2026-10-24). So a cap written by the hook should apply from the first request. Only the cap matters for the trial, because the picker's level always wins over `effortLevel` in an app-opened session (`PL-HYRM` § "Unknown 2").
- Draw from a hash of the `session_id` that the hook receives on standard input, rather than from `secrets`. The hook also runs on resume, and a hash gives a resumed session the same arm rather than a new draw partway through.
- The setup script's `tools/effort_trial.py` line is then removed in the environment's settings. Until it is, the hook overwrites whatever a rebuilt snapshot carries.
- Reword the digest line so that a session reports it in plain words. For example: "This session is in the effort trial's high arm, so it runs at high effort whatever the app's picker shows." Or: "This session is not in the effort trial, because no effort cap was set. It runs at the level the app's picker chose."

**Measure before building.** The docs imply the reload applies a cap written mid-start, but they do not state it, and the hook races the first request. One probe settles it. A branch adds a `SessionStart` hook that writes `"maxEffortLevel": "high"`. The owner opens one session on that branch from the app, with the picker at `xhigh`. The session reads `perTurnEffort` from its own transcript for the first turn and a later one. If both read `high`, build the route above. If the first reads `xhigh`, the first turn is uncapped, and that cost goes back to the owner before anything is built. `PL-HYRM`'s auto mode refused a session's commit of a probe settings file without the owner's word, so the probe needs that word.

**Decision needed.** Reopen the trial's ratified mechanism, which drew the arm in the setup script (project owner, 2026-10-19, ratified), on the caching evidence above, and run the probe? **Recommendation: yes.** The trial is collecting nothing as it stands, and from about 2026-10-30 it would assign one arm per week.

**Decision** (project owner, 2026-10-24, ratified, over keeping the draw in the setup script, which a cached environment skips, and over making the setup script too slow to cache, which would add five minutes or more to every session start). Move the draw into the `SessionStart` hook, keyed on the hook's `session_id`, and reword the digest line, once the probe above shows the cap applies from the first turn. The owner also keeps the app's effort picker at `xhigh` for the length of the trial.

**The probe.** Branch `claude/pl-8mz9-probe-hook-cap` is never merged. Its first `SessionStart` hook writes `"maxEffortLevel": "medium"` to `.claude/settings.local.json` and logs the time to `/tmp/probe-cap.log`. `medium` is below both the app's `xhigh` and `.claude/settings.json`'s `high`, so it tells a capped turn from an uncapped one in a session the app opened and in one `create_session` started. Each probe session reports `CLAUDE_EFFORT` and the top-level `perTurnEffort` field of every assistant record in its own transcript, `/root/.claude/projects/-home-user-open-anesthesia-sim/*.jsonl`.

**Probe result, 2026-10-24: the cap applies from the first turn, in a session `create_session` started.** Probe session `session_016eGqySSBtxtxrF4322XB3i` (transcript `c2bd5b4d-bd26-512d-9475-541af23fdd0e`) ran on `claude/pl-8mz9-probe-hook-cap`. The hook wrote the cap at 3:09:00.7 pm CDT, and the first request went out 23 seconds later. Every assistant record, the first at 3:09:23.8 pm CDT included, carries `"perTurnEffort": "medium"`, and `CLAUDE_EFFORT` read `medium`. Without the cap, `.claude/settings.json`'s `high` would have applied. So a cap that the `SessionStart` hook writes holds from the first turn.

Two things the fix must handle, both seen in the same probe:

- **The hooks run in parallel.** The digest's effort line, run from `.claude/hooks/docket-digest.sh`, reported "none" even though the probe hook had written the file. So the draw and the line that reports it must be one script that writes first and reports second, not two hook entries.
- **`digest_line` gives the wrong reason for a value outside the two arms.** It says the file "sets no maxEffortLevel" whenever the value is not `high` or `xhigh`, including when the file sets `medium`.

**Probe result in a session opened from the app, 2026-10-24: the cap applies from the first turn there too.** The app passes `--effort xhigh` on Claude Code's command line. The owner opened probe session `session_01VDYJtx5U5qqed37FQZtXwF` from the app on the probe branch, with the picker at `xhigh`. The hook wrote the cap at 3:28:43.6 pm CDT. The session's first and only assistant record, at 3:29:07.3 pm CDT, carries `"perTurnEffort": "medium"`, and `CLAUDE_EFFORT` read `medium`. Its digest again reported "none" although the file held the cap, which is the parallel-hook race below.

**Built, 2026-10-24, on `claude/pl-8mz9-hook-draws-effort-arm`.** `.claude/hooks/docket-digest.sh` pipes the hook's JSON input into `python3 tools/effort_trial.py session-start`. That one command writes the arm as `effortLevel` and `maxEffortLevel` in `.claude/settings.local.json`, and then prints the line naming it. The arm is `xhigh` when the SHA-256 digest of the hook's `session_id`, read as a whole number, is divisible by 4, and `high` otherwise. The hook's `session_id` is the transcript's id: this session's is `0ab1bc6b-c99e-5501-9804-99cdd5de3c71`, the name of its transcript file. A resumed or compacted session keeps its id, so it gets the same arm again. The model review can also recompute an arm from that id.

The lines now read "Effort trial: this session is in the high arm. The session-start hook capped its effort at high, so it runs at high unless the app's effort picker is set lower." or, with no arm, "Effort trial: this session is in neither arm, because" followed by the real reason. That reason is the hook's own outcome, not a re-read of the file, so the wrong "sets no maxEffortLevel" reason cannot recur.

Four choices made while building it, each the session's own:

- **Cloud sessions only.** The script does nothing unless `CLAUDE_CODE_REMOTE` is `true`. The docs say that variable is `true` in a cloud session and "never `true` locally" (*Configure cloud environments*, § "Install dependencies with a SessionStart hook", https://code.claude.com/docs/en/cloud-environments.md, read 2026-10-24). A hook runs on the owner's own computer too. Without the check it would have written a cap into their local settings file, where it would have capped every later local session.
- **No random fallback.** A hook input with no session id draws nothing and says so, because a random draw would give a resumed session a new arm.
- **The `CLAUDE_EFFORT` clause is gone from the line.** This session's line carried no "running at" clause, so the hook's environment did not hold `CLAUDE_EFFORT`, while this session's Bash environment reads `xhigh`. And where the hook does see it, the value predates the cap the hook has just written. The review's second result now takes the level a session ran at as the lower of its arm and the app's requested level (`PL-63CB` § "Effort monitoring", step 6, updated here).
- **`/tmp/effort-trial.log` is no longer written.** The printed line carries the outcome and any error, which the log only repeated.

Running the script with no arguments, which the setup script still does, now does nothing but print a note to standard error. That setup-script line can be removed at any time. Until then it is harmless.

**Done when.** The probe's result is recorded here. If the cap applies from the first turn, the `SessionStart` hook assigns the arm, `tests/unit/test_effort_trial.py` covers the hash draw and the reworded lines, `docs/maintainer.md` and `docs/apparatus.md` describe the hook route, and the owner has the steps to remove the setup-script line, which no longer does anything. If it does not, this item records what the first turn costs and the owner's answer.

**Generator check.** One defect in one mechanism, found while answering the owner's question. It explains no other open item.
