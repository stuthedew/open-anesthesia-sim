---
id: PL-HYRM
title: Assign each new cloud session's effort automatically for the effort trial: the cloud environment's setup script, which runs before Claude starts, draws xhigh for about one session in four and high otherwise, writes it as effortLevel in .claude/settings.local.json, and records the draw where the model review can read it; first test that a cloud session applies it
priority: P2
effort: S
status: done
classes: session-cost, infra
feature: model-evidence
touches: docs/maintainer.md, docs/items/PL-63CB-add-a-model-review-skill-that-on-a-cadence-and.md, docs/apparatus.md, tools/effort_trial.py, tests/unit/test_effort_trial.py, .claude/hooks/docket-digest.sh
added: 2026-10-19
closed: 2026-10-19
pr: 1678
payoff: the randomized effort trial runs without the owner setting a level by hand, so its result can say whether high causes real problems
verify: grep -q 'The effort trial starts' docs/maintainer.md
---

**Problem.** Assign each new cloud session's effort automatically for the effort trial: the cloud environment's setup script, which runs before Claude starts, draws xhigh for about one session in four and high otherwise, writes it as effortLevel in .claude/settings.local.json, and records the draw where the model review can read it; first test that a cloud session applies it

**Why it matters.** The owner chose a randomized effort trial on 2026-10-19: about one
session in four at `xhigh`, the rest at `high`, starting after Friday
2026-10-23 at 11 pm CDT. They said setting the level by hand at each session
is not feasible and asked for it to happen automatically (project owner,
2026-10-19). `docs/maintainer.md` § "Match effort to the standard the work is
held to" records the trial, and `PL-63CB` § "Effort monitoring" analyzes it.

**What the docs say.** Claude Code resolves a session's effort in this order:
an explicit choice (`CLAUDE_CODE_EFFORT_LEVEL`, `--effort`, or `/effort`), then
settings (`modelSettings` or `effortLevel`), then the model's default. A
top-level `effortLevel` in project, local or managed settings applies to every
model, and accepts `low`, `medium`, `high` and `xhigh` but not `max` (Claude
Code docs, *Model configuration*, section "Adjust effort level",
https://code.claude.com/docs/en/model-config, read 2026-10-19). The cloud
environment's setup script runs as root after the repository is cloned and
before Claude starts, each time a container is built fresh.

**Proposed route.** The setup script draws a random number. With probability
1/4 it writes `{"effortLevel": "xhigh"}` to `.claude/settings.local.json`,
which outranks `.claude/settings.json`, and otherwise writes `high`. It also
records the draw so the model review can analyze by assignment, not only by
the level that ran.

**Unknowns to test before the trial starts.**
1. Does a level in `.claude/settings.local.json` apply in a cloud session
   started from the app? Test: set it by hand in one fresh session's setup,
   then read that session's effort with `get_session`.
2. Does the app's effort picker count as an explicit choice that overrides
   the file? If it does, the owner must leave the picker alone during the
   trial, and the model review counts the sessions where they did not.
3. Where can the draw be recorded so that it outlives the container? For
   example, the setup script might see the session id, or the session-start
   hook could print the assignment so the session writes it into its own
   commit trailer.

Changing the setup script changes the cloud environment, which the owner
approves through the harness's approval prompt.

**Checked 2026-10-19, before any test.** These facts come from `list_sessions`,
this session's own environment and `docs/session-ledger.tsv`:

- Every session the owner opened from the app or the phone carries
  `session_context.effort_level`, and in the rows read it is `high`. The
  ledger's 2026-08-22 row reads `high` too, a month before
  `.claude/settings.json` set any level. So the app most likely sends a level
  with every session it opens. The docs rank an explicit choice above
  settings, so the file route may do nothing for app-opened sessions. That
  makes unknown 2 the deciding test, not a detail.
- A session started with `create_session` carries no
  `session_context.effort_level`. Inside it, the tools' shell sees
  `CLAUDE_EFFORT=high`, which matches `.claude/settings.json`, and no
  `CLAUDE_CODE_EFFORT_LEVEL`.
- The ledger's `effort_level` column copies `session_context.effort_level`.
  That is the level the app asked for, which may not be the level that ran.
  An analysis by level actually run cannot rely on that column alone.
- The cloud environment is the owner's `Default` personal environment, and its
  setup script installs `uv`, `poppler-utils` and `libegl1`. It writes no
  settings today.
- Auto mode refused this session's commit of a probe
  `.claude/settings.local.json` on a throwaway branch, as the session
  modifying its own settings. So the test needs the owner's word first.

**Unknown 1, measured 2026-10-19: yes, for a session nothing else sets.** The
owner approved a probe. Branch `claude/pl-hyrm-probe-settings-local` adds
`.claude/settings.local.json` with `"effortLevel": "xhigh"` to `main`, whose
`.claude/settings.json` says `high`. A session started on that branch with
`create_session` (`session_01CCoYCwWA4q5xqwsw4FpdUt`) printed
`CLAUDE_EFFORT=xhigh` and `CLAUDE_CODE_EFFORT_LEVEL=unset`. This session, on
`main` with no local file, prints `CLAUDE_EFFORT=high`. So Claude Code read the
local file over the project file, as the docs say, and exports the level it
settled on as `CLAUDE_EFFORT`. That variable is the only place the level showed
up. `get_session` on the probe returns no `effort_level` at all, so the brief's
plan to read the level with `get_session` does not work for a session the app
did not open. The model review needs another record of the level actually run.

**Unknown 2, measured 2026-10-19: the app's picker wins over the settings
files.** The owner opened a session from the app on `main` with the picker at
Medium, and it printed `CLAUDE_EFFORT=medium` against `.claude/settings.json`'s
`high`. Every app-opened session records an effort level, so the app most
likely always sends its picker's level. A setup script that writes only
`effortLevel` would then change nothing in an app-opened session. Managed
settings do not help either. The docs place a managed `effortLevel` at the
same settings step, and "users can still change the level with `/effort` or
`--effort`" (*Model configuration*, section "Set the effort level",
https://code.claude.com/docs/en/model-config.md, read 2026-10-19).

**What does beat the picker is a cap.** `maxEffortLevel` caps "the effort
level a session can use … Any higher level runs at the cap instead, including
one from `/effort`, the `/model` picker, `--effort`,
`CLAUDE_CODE_EFFORT_LEVEL`, a skill's or subagent's `effort` frontmatter, or
the model's own default." Its scope is "Any file", so
`.claude/settings.local.json` can carry it, and "when several scopes set a
cap, the lowest applies". It needs Claude Code v2.1.267 or later, and the
cloud containers run 2.1.303 (*Settings reference*, section `maxEffortLevel`,
https://code.claude.com/docs/en/settings-reference.md, read 2026-10-19). So the
trial can run with the picker left at `xhigh`. The setup script writes
`"maxEffortLevel": "high"` in three sessions of four and no cap in the fourth.
It also writes `effortLevel` to match, for sessions the app does not open.
**The cap route, measured 2026-10-19: the cap beats the app's picker.** Branch
`claude/pl-hyrm-probe-cap` adds `.claude/settings.local.json` with
`"effortLevel": "xhigh"` and `"maxEffortLevel": "high"` to `main`. Two
sessions ran on it:

| Session | Level asked for | `CLAUDE_EFFORT` |
| --- | --- | --- |
| Started with `create_session` (`session_01MtGAZv6FJkkDXfeTycw9yw`) | file `xhigh` | `high` |
| Opened by the owner from the app | picker `xhigh` | `high` |

So `CLAUDE_EFFORT` reports the level after the cap, and the cap limits a
level the app sends. Neither session saw any message saying the level was
capped. A capped session runs at `high` without saying so, which is what the
trial needs.

**Subagents follow their session's arm (docs, not measured).** A subagent's
`effort` frontmatter "Overrides the session effort level", and the Agent
tool's per-call `effort` parameter overrides that (*Subagents*, "Supported
frontmatter fields" and "Choose an effort level",
https://code.claude.com/docs/en/sub-agents.md, read 2026-10-19). So a subagent
with neither runs at its session's level. The docs imply that rather than
state it. A cap "still limits the level the skill or subagent runs at"
(*Model configuration*, "Adjust effort level"). This repository's one
subagent definition, `.claude/agents/Explore.md`, sets no `effort`, and
`docs/maintainer.md` forbids a session from asking a subagent for a lower one.
So a capped session's subagents run at `high`, even when a higher level is
asked for. An uncapped session's subagents run at `xhigh` unless a session
asks for `max`.
The unit stays the session together with its subagents. A subagent's level
cannot be read from `CLAUDE_EFFORT`: the variable belongs to the session's
process, and a subagent runs inside that process.

**Decision (project owner, 2026-10-19, ratified, over a setup script that
writes only `effortLevel`, which the app's picker overrides, and over running
the trial only on sessions a coordinator starts).** The trial uses the cap
route. The owner leaves the app's effort picker at `xhigh` for the length of
the trial. In about three sessions of four, `.claude/settings.local.json` gets
`"effortLevel": "high"` and `"maxEffortLevel": "high"`. In the fourth it gets
`"effortLevel": "xhigh"` and `"maxEffortLevel": "xhigh"`. The second cap stops
a subagent asked for `max`, or a Max picked in the app by mistake, from running
above the arm. The start is unchanged: nothing is written before Friday
2026-10-23 at 11 pm CDT (2026-10-24 04:00 UTC), when the owner's weekly usage
resets. Still unanswered: whether the app keeps the picker's last level for
new sessions.

**Decision (project owner, 2026-10-19): every session tells the owner its
arm.** The owner said that blinding them buys nothing: the model review takes
the outcomes from the record (rework items, recurrences, red CI runs,
review-bot findings, churn) and judges nothing by hand. The recommendation
below assumed the owner judged the outcomes, which was wrong. The cap also
keeps the owner from raising a capped session's level, so knowing the arm
cannot change the level a session runs at. Build the hook line described
below. The analysis notes that the owner was told each session's arm.

**The question as it was put (asked 2026-10-19): should a session tell the
owner its arm?** The picker will read `xhigh` in every session, so nothing on
screen shows a capped one. A session can announce its level cheaply. The
`SessionStart` hook already prints the digest. It could add one line built
from `CLAUDE_EFFORT`, such as "Effort: high (trial arm)", and the session
would repeat it in its first reply.
*Recommendation: do not announce it during the trial.* The owner reviews the
work and files most of the outcomes the analysis counts: rework items, review
findings and reopenings. Knowing which sessions ran at `high` can change how
closely the owner reviews them and how often the owner raises their level.
That biases the comparison in a way the analysis cannot remove. This is why
trials blind whoever assesses the outcomes (Schulz KF, Grimes DA, "Blinding in
randomised trials: hiding who got what", *Lancet* 2002;359:696-700). The arm
is still recorded and shown in the monthly model review, so nothing is lost.
If the owner wants it shown anyway, build the hook line, and have the analysis
say that the trial was not blinded.

**Built 2026-10-19.**

1. `tools/effort_trial.py`, with `tests/unit/test_effort_trial.py`. The
   setup script runs it with no argument. It draws `xhigh` with probability
   1/4 using `secrets`. From 2026-10-24 04:00 UTC it writes the arm as
   `effortLevel` and `maxEffortLevel` in `.claude/settings.local.json`, and
   it logs every run to `/tmp/effort-trial.log`.
2. The cloud environment's setup script (the owner's `Default` environment)
   gained one line, approved by the owner on its card:
   `f=/home/user/open-anesthesia-sim/tools/effort_trial.py; [ -f "$f" ] && python3 "$f" || true`.
   It does nothing in a checkout without the file, so it is harmless in other
   repositories and on branches cut before this one merged.
3. `.claude/hooks/docket-digest.sh` runs `tools/effort_trial.py digest`
   early in the session-start digest. From the start time it prints
   "Effort trial arm: high." or "xhigh.", says the cap holds whatever the
   picker shows, adds the level in `CLAUDE_EFFORT` where the hook's
   environment holds it, and tells the session to give the owner the arm in
   its first reply. No rule set what a first reply contains, so the
   instruction rides in the digest line itself rather than in a resident
   file. Where no arm was written it says so and why.
4. `docs/maintainer.md` § "Match effort to the standard the work is held to"
   gives the start time and how the trial works. `PL-63CB` § "Effort
   monitoring" step 6 says where the arm is recorded and how to read it.
   Its new step 7 is the stopping point: the review puts ending the trial to
   the owner once both arms have adequate data, and at its 2027-04-24 run in
   any case. That date is a placeholder set here for the owner to change.
5. Three scheduled tasks, each starting a fresh session
   with push and email notifications. Each prompt attaches the repository
   itself, because a scheduled session starts with none (`sources: []` in
   the task as created).
   - "PL-HYRM: is the effort trial ready to start Friday night?"
     (`trig_01ANGyWDXegBT6pScgaBJ2Gu`), Thursday 2026-10-22, 9:00 am CDT.
   - "Effort trial has started: announce and check"
     (`trig_01Vcr2WJZKiCz3DXt3jtidCF`), 2026-10-24 04:05 UTC (Friday
     11:05 pm CDT). This is the owner's one-time start announcement. It
     fires once by construction, so it needs no record of having fired. It
     also starts a probe session on `main` and reports whether that
     session's arm line, log and settings agree, which is the end-to-end
     test of the live trial.
   - "Monthly effort-trial review" (`trig_01U72kAfYGB494ZuQL1UQaHs`),
     `CRON_TZ=America/Chicago 47 8 24 * *`. Its 2026-10-24 run replies in one
     line and stops, so the first real review is 2026-11-24. It runs
     `PL-63CB`'s skill if built, and its § "Effort monitoring" by hand if not.

**Unknown 3, measured: the setup script cannot see the session id.** A probe
session on this branch (`session_01E73NmN5Ye3r6BGgszscooh`, 2026-10-19 21:58
UTC) logged `no-id`. Its container was a pre-built spare: the setup script ran
at 21:59:20 UTC, before the session claimed it (`warm_spare_claimed: true` in
the probe's result event). The session itself held
`CLAUDE_CODE_REMOTE_SESSION_ID=cse_01E73NmN5Ye3r6BGgszscooh` and
`CLAUDE_EFFORT=high`. So the hash route below cannot run, and the draw is
random. The record is the digest line instead. The probe's own transcript
showed that each hook's output is stored as a `hook_response` event, which
`list_events` returns, so the review can read each session's arm by its
session id. Two limits follow. A container rebuilt for a resumed session draws
again, so the review uses a session's first arm line. And a session deleted
before the review loses its record.

**A route that removes unknown 3 (refuted 2026-10-19; see above).** The draw can be a fixed function of the
session id instead of a stored random number: hash the id, and assign `xhigh`
when the hash falls in the lowest quarter. The ledger already holds every
session id, so the model review recomputes each assignment and nothing new has
to be stored. Online controlled experiments assign by a hash of the unit's id
for the same reason: the assignment is reproducible and needs no lookup table
(Kohavi, Tang and Xu, *Trustworthy Online Controlled Experiments*, Cambridge
University Press, 2020; chapter not checked). It needs the setup script to see the
session id. `CLAUDE_CODE_REMOTE_SESSION_ID` (`cse_...`) shares its suffix with
the ledger's `session_...` id, but whether the setup script's environment holds
that variable is untested.

**Done when.** The three unknowns are answered in this brief. A new cloud
session gets its level from the draw without the owner setting it. The draw is
recorded where the model review can read it. `docs/maintainer.md` gives the
date the trial starts.

**Revised 2026-10-19, when the build ended.** `get_session` shows only the
level the app asked for, and only for a session the app opened, so it cannot
show the arm. The digest line and `CLAUDE_EFFORT` show it instead. The item
closes before the start time so that its pull request can merge in time.
Everything up to the start was tested on 2026-10-19: the tests pin the draw,
the gating and the settings write, and a fresh session showed that the setup
script runs the script. What runs only from the start time, a written cap and
a printed arm line in a live session, is checked by the "Effort trial has
started: announce and check" task. That task reports any failure to the owner
at 11:05 pm CDT on Friday.

**Generator check.** A one-off, asked for by the owner; not a member of a head.
