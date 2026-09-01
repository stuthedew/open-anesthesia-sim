---
id: PL-5KR2
title: A session handed an item by name never reads the in-flight answer, because docket next is the only surface that applies it
status: untriaged
added: 2026-09-01
---

**Problem.** `plan.recommend` excludes in-flight ids outright, and its docstring
says why: "recommending work somebody is doing is worse than recommending
nothing". But that exclusion lives in `recommend`, so it reaches a session only
through `docket next`. The project owner naming an item - "PL-K7QX", the
documented way to start one, and the exact form the `docket` skill's fresh-session
line recommends - skips `next` entirely.

What such a session does run is `bin/docket triage`, `bin/docket check` and
`bin/docket show`. None of them says anything about in-flight work. The
session-start digest carries an `In flight on a branch` line, but it is printed
once, before the item in question was named and often before the branch that
carries it existed.

**Why it matters.** The one guard against two sessions doing the same work is
applied only on the path where the work was *not* chosen by a person. Naming an
item is the higher-confidence path and the one with no guard, which is backwards.

Observed 2026-09-01. A session was handed `PL-QS72`, read the item, read
`checks.py` and `vcs.py`, and was one edit from writing the fix before the owner
asked whether another session might already be on it. Nothing in the commands
that session had run would have said. The answer happened to be no, but it was
reached by the owner asking rather than by the tooling.

**Where.** Two candidate levers, and the second is the cheaper.

- `.claude/skills/docket/SKILL.md`, "Mode: start an item" - it already says to
  rename the session, name the branch and set `status`/`feature`/`touches`. It
  does not say to ask whether the item is in flight. One line, and it fires at
  exactly the right moment.
- `bin/docket show <id>` - the command a session runs to read an item it was
  handed. Marking it `IN FLIGHT` there costs the reader nothing and cannot be
  skipped, which the prose can. `render._marks` already emits that mark for
  `list`, so the machinery exists.

Prefer the second, per `CLAUDE.md`'s routing rule: a check that fires beats prose
a session may not reach. The two are not exclusive.

**Note on the bound.** `docket flight` reads refs, so a session that has not
pushed is invisible to it whatever surface asks. That is a real limit rather than
a defect here - it is the same limit `format_unread` already reports - and the
answer this item wants is "what is knowable", not "what is certain".

**Done when.** A session that reads an item by id, without running `docket next`,
is told when that item is in flight on a branch.
