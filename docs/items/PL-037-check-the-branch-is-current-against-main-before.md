---
id: PL-037
title: Check the branch is current against `main` before starting an item
priority: P2
effort: S
status: ready
classes: session-cost, infra
feature: dev-tooling
touches: .claude/hooks/docket-digest.sh
added: 2026-08-24
verify: bash -n .claude/hooks/docket-digest.sh && .claude/hooks/docket-digest.sh | grep -q "^Branch: "
---

**Problem.** Nothing in `CLAUDE.md` or the punch-list skill tells a session
to verify its branch against `main` before it starts work. A session that
picks up a branch whose pull request has already been merged stacks new
commits on merged history; one that starts from a stale base does the work
against code that has since moved.
**Why it matters.** Both cost a full rework cycle — the most expensive kind
of waste, since it is paid at the end of a session in merge conflicts rather
than at the start in one command. This actually happened: the session that
landed PL-032 was asked to check, found its own branch had been merged as
PR 19, and had to restart the branch from `main` before continuing.
**Where.** `.claude/skills/punch-list/SKILL.md` (a step before "Mode:
recommend what to work on" hands off, and in "Mode: hotfix"), possibly
`CLAUDE.md`'s "Punch list and work selection".
**First step.** Write the check as the three commands it actually takes:
`git fetch origin main`, `git rev-list --left-right --count origin/main...HEAD`,
and — when the branch is behind with nothing ahead — restart it from `main`
rather than merging into it.
**Done when.** The handoff a recommendation produces names the check, so a
fresh session runs it before its first edit rather than discovering the
problem at push time.

**Mechanism changed, 2026-08-30: a check that fires, not a rule to remember.**
The brief above puts the rule in `CLAUDE.md` and the skill. That is the weaker
half of the same idea, and this item is itself the evidence: the rule it asks
for is one more paragraph in documents a session may or may not have loaded at
the moment it matters, and it fires at exactly the moment nobody is thinking
about branches — the start, before any work has made the branch interesting.
A session that would remember to run the check is a session that would not
have needed it.

So the three commands the **First step** names became the content of a check
that runs whether or not anybody remembers it. `.claude/hooks/docket-digest.sh`
already runs every session as a SessionStart hook, so the delivery existed:
it now fetches `origin/main`, reads `git rev-list --left-right --count
origin/main...HEAD`, and prints one line — or three, with the exact commands,
when the branch is behind with nothing of its own, which is what a merged pull
request looks like from the branch's side.

Deliberately in the hook rather than in `docket`: the fetch is a network call
and `docket` is standard-library-only, offline, and deterministic for a given
store. A digest that reached the network would make every command that shares
its code path slower and less predictable.

Nothing was added to `CLAUDE.md` or the skill. A rule saying "run the check"
beside a check that has already run is a second thing to keep true, and this
project's own standard prefers the mechanism to the reminder.

**Stale citation corrected.** The **Where** above cites
`.claude/skills/punch-list/SKILL.md`, which no longer exists; the file is now
`.claude/skills/docket/SKILL.md`. Left in the original paragraph as written,
recorded here — neither file is touched by this item any more.
