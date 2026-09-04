---
id: PL-X3WZ
title: A commit that only annotates an item's brief marks it IN FLIGHT, so docket next hides an item nobody is working
status: needs-decision
added: 2026-09-03
priority: P2
effort: M
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, .claude/skills/docket/SKILL.md
---

**Problem.** `docket flight` recovers in-flight state by parsing commit
subjects for item ids, and `CLAUDE.md` requires every commit subject to lead
with the id of the item it concerns. Those two rules collide on the commit that
records a finding *into* an item's brief without starting the work. Such a
commit is indistinguishable from one carrying the item's implementation, so the
item is marked `IN FLIGHT` and `docket next` excludes it - for every session,
until the branch merges.

**Observed 2026-09-03.** This session recorded a scope note into `PL-DHV7`'s
brief and pushed it. `bin/docket next` had ranked `PL-DHV7` first immediately
before; immediately after the push it moved into "Excluded, already in flight"
and `PL-DR1Z` took the top slot. Nobody was implementing `PL-DHV7`, and the
session that annotated it was in the same breath recommending someone start it.

**Why it matters.** The two rules it sits between are both mandatory and both
frequently exercised: `CLAUDE.md` requires a finding to be captured before the
session ends, requires a behavior change to land in the session that asks for
it, and requires the leading id on every subject. So the collision is not rare -
every annotate-and-push, every `touches` fill, every `verify:` command written
onto an item ahead of the work produces it. The failure is silent and it is in
the direction that costs most: an item is hidden from the queue rather than
offered twice.

It is self-healing on merge, which bounds the harm to a branch's lifetime and
is why this is not urgent. But the shape is wrong - the guard was built to stop
two sessions colliding on one item, and it currently also stops one session
finding an item no session holds.

**Where.** `subprojects/docket/src/docket/` - whatever `branches_in_flight`
and `cmd_next` read; `docket flight`, `docket show` and `docket triage` all
surface the same mark. `.claude/skills/docket/SKILL.md` documents the trade the
mark makes ("an abandoned branch and a live session look alike") and would need
the annotation case added to it.

**Decision needed.** Whether the in-flight signal comes from the diff or from
the commit subject. Recommended: the diff. It asks nothing of a session, so it
cannot be forgotten the way a marker convention can, and it also classifies
`bin/docket new`'s capture commits correctly for free. Take the subject marker
only if the diff read measures too expensive against `PL-PGY4`'s numbers - the
candidate pool is already the slow half of `docket check` - and note that a
convention a session must remember is exactly what `PL-CP74` records failing in
the opposite direction.

**Approach, not yet decided.** Two candidates, and the difference is whether
the signal comes from the diff or from the subject:

1. **Read the diff.** A commit whose changes to that item's file touch only the
   body, or whose changes anywhere are confined to `docs/items/`, is annotation
   rather than implementation. Decidable, no new convention to remember, and it
   also correctly classifies the capture commits `bin/docket new` produces.
   Costs a `git show --stat` per candidate commit, which matters because
   `PL-PGY4` and `PL-9NKK` already measure this pool as the slow half of
   `docket check`.
2. **A subject marker.** A trailer or prefix that says "annotates, does not
   start". Cheap to read, but it is a convention a session must remember, and
   the whole point of parsing subjects was that the id rule is already
   remembered.

Prefer (1) if the cost measures acceptable against the numbers in `PL-PGY4`;
it needs nothing of the session. Worth checking against `PL-CP74`
(housekeeping work carries no item id, so the guard is blind to it) - that item
is the same guard failing in the opposite direction, and one design may answer
both.

**Done when.** A commit that only records a note into an item's brief no
longer marks that item `IN FLIGHT`, and a commit carrying its implementation
still does; `docket next` offers the annotated item on the branch that
annotated it. Whichever route is taken, `.claude/skills/docket/SKILL.md`'s
statement of the trade the mark makes says what the mark now means.
