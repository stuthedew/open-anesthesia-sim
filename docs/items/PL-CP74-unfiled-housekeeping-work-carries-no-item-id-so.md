---
id: PL-CP74
title: Unfiled housekeeping work carries no item id, so every in-flight guard is structurally blind to it
status: untriaged
feature: parallel-sessions
touches: .claude/skills/docket/SKILL.md, CLAUDE.md
added: 2026-09-02
---

**Problem.** `docket flight`, `show`, `triage`, `next` and the session-start
digest all answer "is anybody already on this?" by matching a `PL-` id — in a
commit subject, in a branch name, in a session title. Work that has no item
has no id, so every one of them returns a clean answer for it, correctly and
uselessly.

That is most of what actually collides. The project owner reports the
duplicated work being repository housekeeping rather than queue items:
resolving a merge, clearing a stale `origin/<branch>` ref, a docs sweep, a
lint fix, recovering a stranded item. None of it is filed, all of it is
obvious enough that two sessions independently recommend it in the same hour,
and it is invisible to the guards even *after* both sessions have pushed —
which is the part that separates this from `PL-D4MZ`, where the window closes
once somebody pushes.

**Why it matters.** It is the cheap half of the reported problem and it needs
no new machinery. The existing guards are sound; they are simply never handed
anything to match on. Filing the work first — `bin/docket new`, then start it
under its id, per the skill's existing "Mode: start an item" — puts
housekeeping inside the mechanism the project has already built and paid for
across `PL-5KR2`, `PL-S1P1`, `PL-PRHN` and `PL-SK88`.

It also fixes a second thing for free: unfiled work leaves no record, so the
same housekeeping gets rediscovered and re-recommended by later sessions that
cannot tell it was already done.

**Where.** `.claude/skills/docket/SKILL.md`, and `CLAUDE.md` if the rule has to
fire before a session would think to load the skill — which it probably does,
since a session clearing a stale ref has no reason to open the docket skill at
all. Per `CLAUDE.md`'s routing test, check first whether the decidable part
belongs in a script instead: a pre-push or pre-commit hook can see a commit
subject with no leading id and say so, which costs no resident context and
never fails to fire.

The judgment to keep out of any such check: how small is too small to file.
A rule that demands an item for a one-line typo fix converts the queue into
a log, which is worse than the collisions it prevents.

**Done when.** A session about to do unfiled repository housekeeping has a
stated rule telling it to file the item first and work under its id, and
something deterministic catches the case where it did not.
