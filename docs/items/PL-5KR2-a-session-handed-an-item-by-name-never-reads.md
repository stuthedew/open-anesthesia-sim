---
id: PL-5KR2
title: A session handed an item by name never reads the in-flight answer, because docket next is the only surface that applies it
priority: P2
effort: S
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, .claude/skills/docket/SKILL.md, subprojects/docket/README.md
verify: uv run pytest subprojects/docket/tests/test_cli.py -k "show and flight"
status: done
added: 2026-09-01
closed: 2026-09-01
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

**Note on the bound, sharpened by what happened next.** Two gates, not one, and
the first was the one missed. `docket flight` and `docket show` read the refs
*this checkout already holds* - only `docket branch` calls `fetch_remote` - so
without a `git fetch` the answer is as old as the clone. On top of that, a
session that has not pushed is invisible however fresh the refs are.

Both limits are deliberate rather than defects: a read command that reached the
network would stop working in the bare, offline checkout `docket` is built to
run in, and `merged_pull_requests` records the same stance ("Deliberately no
fetch"). So the answer this wants is "what is knowable", not "what is certain",
and the surface must say which.

The live case, 2026-09-01, is why the fetch half matters. This session ran
`bin/docket flight` and was told no branch carried an item id. Four minutes
later pull request 151 opened on `PL-QS72` from a branch that had been pushed
in between; after `git fetch`, `flight` reported it correctly. Nothing was
broken - the ref simply was not here yet. The owner asked the question the
tooling had not been asked to.

**Done when.** A session that reads an item by id, without running `docket next`,
is told when that item is in flight on a branch.

**Triaged 2026-09-01, and both levers are taken.** The brief above prefers the
`show` mark over the skill line, on `CLAUDE.md`'s routing rule that a check
which fires beats prose a session may skip. That ordering is wrong for this
particular gap, and the session that found it is the counter-example: it had
the `docket` skill loaded and still did not ask, because "Mode: start an item"
does not say to - and it read the item with `cat`, not `bin/docket show`, which
the skill itself permits ("Read an item's file when implementing it"). A mark
on a command nobody is obliged to run does not fire.

So the skill line is the reliable trigger and the `show` mark is the check that
catches the session which does use the command. Both, with the prose leading -
which is the rare case where routing to `.claude/` beats routing to a script,
because the moment the rule has to fire is a decision a session makes before it
runs anything.

`P2`, `parallel-sessions`, beside `PL-S1P1`, `PL-CPSY` and `PL-3576`: it is the
same seam - the in-flight answer reaching the surfaces that need it - and this
is the surface with no reader at all rather than one reading it partially.

`show` must print `format_unread` too once it marks, per that function's own
rule that every command ranking or marking against in-flight ids says which
refs went unread. A mark without it presents a bounded answer as a complete
one, which is what the **Note on the bound** above is about.

The `verify:` selector exits 5 on 2026-09-01: no test in `test_cli.py` carries
both `show` and `flight`.
