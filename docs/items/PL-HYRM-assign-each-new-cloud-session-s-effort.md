---
id: PL-HYRM
title: Assign each new cloud session's effort automatically for the effort trial: the cloud environment's setup script, which runs before Claude starts, draws xhigh for about one session in four and high otherwise, writes it as effortLevel in .claude/settings.local.json, and records the draw where the model review can read it; first test that a cloud session applies it
priority: P2
effort: S
status: ready
classes: session-cost, infra
feature: model-evidence
touches: docs/maintainer.md, docs/items/PL-63CB-add-a-model-review-skill-that-on-a-cadence-and.md
added: 2026-10-19
payoff: the randomized effort trial runs without the owner setting a level by hand, so its result can say whether high causes real problems
verify: grep -qi 'effort trial started' docs/maintainer.md
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

**A route that removes unknown 3.** The draw can be a fixed function of the
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
session gets its level from the draw without the owner setting it, and
`get_session` shows that level. The draw is recorded where the model review
can read it. `docs/maintainer.md` gives the date the trial started.

**Generator check.** A one-off, asked for by the owner; not a member of a head.
