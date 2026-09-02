---
id: PL-PRHN
title: bin/docket triage names no in-flight refs, so two sessions triaged the same two items concurrently and collided at merge
status: untriaged
added: 2026-09-02
---

**Problem.** `bin/docket show <id>` marks an item `IN FLIGHT` and names the refs
it could not read - the guard the `docket` skill calls "the one step with no
other guard" before starting an item. `bin/docket triage` has no equivalent. It
lists the untriaged items and the rules their answers must satisfy, and says
nothing about whether another branch is already triaging them.

**Why it matters.** Observed 2026-09-02. This session ran `git fetch origin` and
then `bin/docket triage`, was told `PL-B0YN` and `PL-LXR3` were untriaged, and
triaged both. Another session was triaging the same two items and landed first
(#186, #188). The result was two conflicting resolutions of the same two files
and a merge that had to discard most of one session's work - including a
`verify:` command for `PL-LXR3` that would have added 7.5-9.5 s to every
`make check`, which the other session had explicitly reasoned its way out of.

Triage is more exposed to this than starting an item, not less. Starting an item
is preceded by `docket show`, which warns; triage is the entry point a session
reaches straight from the session-start digest, which reports the untriaged
count and nothing about who is holding it. The digest itself already knows -
it prints "In flight on a branch: ..." - so the information exists and simply is
not on this path.

**Where.** The `triage` command in `subprojects/docket/src/docket/cli.py`, beside
the rules block it already prints; `vcs.py` carries the in-flight machinery
`show` and `flight` use, so nothing new has to be computed.

**Approach.** Print the same in-flight line `show` prints, per item, and name the
refs that could not be compared - a session that sees "PL-LXR3 is in flight on
claude/..." stops before writing. Whether it should refuse outright or only warn
is worth deciding: triage is cheap to redo and a hard refusal would block a
session whose branch is the one holding the item.

**Note.** The guard is bounded by what has been pushed, exactly as `show`'s is,
so it would not have caught this collision if the other session had not yet
pushed. It is still the difference between a silent collision and a visible one.

**Done when.** `bin/docket triage` names, for each untriaged item it lists,
whether a branch already carries it, and says which refs it could not read; and
a test pins that an item in flight is reported rather than listed silently.
