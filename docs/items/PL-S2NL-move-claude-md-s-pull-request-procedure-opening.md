---
id: PL-S2NL
title: Move CLAUDE.md's pull request procedure (opening, arming, bringing main in, repeated CI failures) into a skill, keeping one always-loaded trigger sentence and a hook on push and pull request creation
status: untriaged
feature: skill-routing
added: 2026-10-24
---

**Problem.** Move CLAUDE.md's pull request procedure (opening, arming, bringing main in, repeated CI failures) into a skill, keeping one always-loaded trigger sentence and a hook on push and pull request creation

**Why it matters.** Two bullets in `CLAUDE.md` § "The queue, and how the project owner works" carry the pull request procedure: "Commit and push as you go" and "Bring `origin/main` into an open pull request once". A rough split on 2026-10-24 measured them at 4,008 and 1,190 characters. Every session loads them, but only a session about to push or open a pull request needs them. Here the trigger is a tool call, so a hook can start the skill reliably instead of relying on the model to remember. `.claude/hooks/push-check-guard.sh` and `.claude/hooks/pr-body-email-guard.sh` already run at those moments.

**Waits on** `PL-SN2Z`, which tests whether our skills start when they should. If it shows that a one-sentence trigger is not enough, the hook carries the start. Work this item after `PL-6VJ3` and `PL-JRVV`, which also edit `CLAUDE.md`, so that no paragraph is moved by one item and deleted by another.

**What stays always loaded.** Any rule a session must apply before its first commit or push stays: the item id at the front of every commit subject, and the `Co-authored-by` line. The read-only rule that a session disarms its own armed pull requests also stays, because it applies before any push.

**Done when.** The procedure lives in a skill. `CLAUDE.md` keeps one trigger sentence and a pointer. The hooks on push and on pull request creation name the skill. `docs/resident-instructions.md` records the move, and `make check`'s resident total shows the cut.
