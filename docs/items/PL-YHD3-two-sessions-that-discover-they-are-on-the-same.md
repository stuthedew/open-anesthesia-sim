---
id: PL-YHD3
title: Two sessions that discover they are on the same work have no rule for which one yields
priority: P2
effort: S
status: done
classes: infra
feature: parallel-sessions
touches: .claude/skills/docket/SKILL.md, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py
added: 2026-09-02
closed: 2026-09-04
verify: python3 tools/doc_check.py check && grep -qF 'which session yields' .claude/skills/docket/SKILL.md && uv run pytest subprojects/docket/tests/test_vcs.py && grep -q 'def test_precedence' subprojects/docket/tests/test_vcs.py
---

**Problem.** Everything the project has built for parallel sessions is
*detection*: `docket show` marks an item `IN FLIGHT`, `docket triage` names the
refs it could not read, `docket next` excludes what is in flight, the skill
adds a session-list scan. Nothing says what the second session should then
*do*, and nothing says which of the two is the second.

So the collision is discovered late — usually as a merge conflict, after both
sessions have paid in full — and the resolution is improvised each time.

**Why it matters.** The project owner asked for exactly this as the acceptable
fallback: if two sessions cannot be stopped from starting the same work, let
them discover it and "gracefully have only one complete the task, ideally as
efficiently as possible". It is worth having even if `PL-D4MZ` produces a
working reservation mechanism, because the `docket` skill already records that
prevention has an irreducible gap: "two sessions starting in the same minute
still race, because both answers come from refs."

Symmetry is the failure mode a rule has to remove. Without a deterministic
tiebreak, both sessions reason the same way from the same evidence and either
both continue — the collision proceeds — or both stand down, which is worse,
because the work is now unstarted and each session believes the other has it.

**Where.** `.claude/skills/docket/SKILL.md`, "Mode: start an item", after the
existing `git fetch origin` / `docket show` / session-list guard. Two pieces:

- **A tiebreak that both sessions compute identically** from evidence both can
  see. Earliest push wins is the obvious candidate and matches the direction
  the project already leans, since it rewards `PL-SK88`'s "push the first
  commit as soon as there is one". Where neither has pushed, the session list
  carries creation times.
- **What yielding costs.** The loser stops, does not push, says in its reply
  which branch it yielded to and what it had already found, and hands over
  anything the winner would otherwise redo — a diagnosis, a failing test, a
  root cause. A yield that discards the work done up to that point is a
  session thrown away; a yield that hands it over is a session spent on
  reconnaissance, which is a different price entirely.

Where the second session has already produced most of the work, the honest
answer may be that the *winner* yields. Whether the rule needs that case, or
whether the added judgment costs more than the sessions it saves, is the
open question here.

**Done when.** A session that finds another on the same work can determine
without further evidence whether it is the one that continues, and the one
that stops has a stated way to hand over what it found.
