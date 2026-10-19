---
id: PL-HYRM
title: Assign each new cloud session's effort automatically for the effort trial: the cloud environment's setup script, which runs before Claude starts, draws xhigh for about one session in four and high otherwise, writes it as effortLevel in .claude/settings.local.json, and records the draw where the model review can read it; first test that a cloud session applies it
priority: P2
effort: S
status: untriaged
classes: session-cost, infra
feature: model-evidence
touches: docs/maintainer.md, docs/items/PL-63CB-add-a-model-review-skill-that-on-a-cadence-and.md
added: 2026-10-19
payoff: the randomized effort trial runs without the owner setting a level by hand, so its result can say whether high causes real problems
verify: grep -q PL-HYRM docs/maintainer.md
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

**Done when.** The three unknowns are answered in this brief. A new cloud
session gets its level from the draw without the owner setting it, and
`get_session` shows that level. The draw is recorded where the model review
can read it. `docs/maintainer.md` gives the date the trial started.

**Generator check.** A one-off, asked for by the owner; not a member of a head.
