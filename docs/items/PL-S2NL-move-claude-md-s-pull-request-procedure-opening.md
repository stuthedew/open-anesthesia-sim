---
id: PL-S2NL
title: Move CLAUDE.md's pull request procedure (opening, arming, bringing main in, repeated CI failures) into a skill, keeping one always-loaded trigger sentence and a hook on push and pull request creation
priority: P2
effort: M
status: blocked
classes: session-cost
feature: skill-routing
touches: CLAUDE.md, .claude/skills, .claude/hooks/push-check-guard.sh, .claude/hooks/pr-body-email-guard.sh, docs/resident-instructions.md
blocked-by: PL-6VJ3, PL-JRVV
added: 2026-10-24
---

**Problem.** Move CLAUDE.md's pull request procedure (opening, arming, bringing main in, repeated CI failures) into a skill, keeping one always-loaded trigger sentence and a hook on push and pull request creation

**Why it matters.** Two bullets in `CLAUDE.md` § "The queue, and how the project owner works" carry the pull request procedure: "Commit and push as you go" and "Bring `origin/main` into an open pull request once". A rough split on 2026-10-24 measured them at 4,008 and 1,190 characters. Every session loads them, but only a session about to push or open a pull request needs them. Here the trigger is a tool call, so a hook can start the skill reliably instead of relying on the model to remember. `.claude/hooks/push-check-guard.sh` and `.claude/hooks/pr-body-email-guard.sh` already run at those moments.

**What `PL-SN2Z` found, 2026-10-24.** A skill named by a resident trigger started first in 8 of 8 sessions whose request named its moment. It measured no moment that arrives mid-task, which is this procedure's, so keep the hooks on push and on pull request creation. Keep a resident sentence that names the moment, and name it in the skill's description too.

**Waits on** `PL-6VJ3` and `PL-JRVV`. Work this item after `PL-6VJ3` and `PL-JRVV`, which also edit `CLAUDE.md`, so that no paragraph is moved by one item and deleted by another.

**What stays always loaded.** Any rule a session must apply before its first commit or push stays: the item id at the front of every commit subject, and the `Co-authored-by` line. The read-only rule that a session disarms its own armed pull requests also stays, because it applies before any push.

**Done when.** The procedure lives in a skill. `CLAUDE.md` keeps one trigger sentence and a pointer. The hooks on push and on pull request creation name the skill. `docs/resident-instructions.md` records the move, and `make check`'s resident total shows the cut.

**Generator check.** None. The owner asked for this work after the comparison with testdouble/han, and no fact was misread to produce it.
