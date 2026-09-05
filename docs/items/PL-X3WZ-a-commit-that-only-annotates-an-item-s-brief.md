---
id: PL-X3WZ
title: A commit that only annotates an item's brief marks it IN FLIGHT, so docket next hides an item nobody is working
priority: P2
effort: M
status: done
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/README.md, .claude/skills/docket/SKILL.md
added: 2026-09-03
closed: 2026-09-05
pr: 324
verify: uv run pytest subprojects/docket/tests/test_vcs.py && grep -q 'def test_a_commit_that_only_writes_to_the_queue_is_not_work' subprojects/docket/tests/test_vcs.py
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

**Measured again 2026-09-04, and it is worse than one item.** A triage session
ran `bin/docket next`: it excluded nine items as in flight, and **eight of the
nine marks come from commits whose entire diff is inside `docs/items/`**. Only
`PL-FX3N` was actually being implemented on a branch.

| Commit | Diff | Ids it marked |
| --- | --- | --- |
| `fe474d4` "PL-HKF4, PL-PGZK, PL-5WFS, PL-22Z3: recover the stranded capture" | 7 files, all `docs/items/` | 4 |
| `d36dabd` "PL-WW08, PL-PMT7: recover two captures stranded on abandoned branches" | 5 files, all `docs/items/` | 2 |
| `067110a` "PL-55JM: capture drift.yml's two serial pytest runs" | 1 file, the item itself | 1 |
| `33b79c6` "PL-N5WZ: record `pr: 265`" | 1 file, a `docket record` write | 1 |

Three of the eight are open and startable, and were hidden from every session's
`docket next` for it: `PL-5WFS` (a brief's stated blocker is invisible to
`next`), `PL-HKF4` (`doc_check`'s tag advisory prints an unpasteable
`<merge commit>`), `PL-PGZK` (`concurrent`'s answer is dominated by docs).

**A batch commit hides a batch of items.** `fe474d4` marked four ids at once.
The `CLAUDE.md` rule that a closure leads with every id it closes, and
`stranded`'s own recovery workflow, both produce multi-id subjects - so one
housekeeping push routinely removes several items from the queue together.

**"Self-healing on merge" does not hold for the branch that produces most of
them.** Both branches carrying six of the eight marks belong to archived
sessions whose last recorded action was *asking whether to open a pull
request*; neither ever did. A branch nobody merges never heals, so the harm is
bounded by nothing - which is the same accumulation `PL-64LS` built `docket
stranded` to recover from. That materially weakens this item's own "not urgent"
in the paragraph above.

**Triage is self-defeating under this.** The point of triaging an item to
`ready` is to let `docket next` offer it; the triage commit is what then hides
it from `docket next` until merge. `PL-55JM` also demonstrates the read side:
it carried the mark, so `bin/docket triage` told that session to skip the only
item it had to do. Proceeding took three independent checks that the tool could
have made itself - the branch's copy of the item file was byte-identical to
`main`'s, the commit that marked it changed nothing but that file, and the live
session on that branch was working `PL-FX3N`.

**The diff read this evidence supports is narrower than option 1 below.** Every
one of the eight false marks is a commit changing *only* `docs/items/`, so
"confined to `docs/items/`" alone separates all eight without needing to inspect
which part of an item's file changed. That is one `git show --stat` per
candidate commit and no body-vs-frontmatter parsing.

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

---

**Decided 2026-09-05: the diff, per the recommendation above, and the cost
objection turned out not to arise.** The route this item costed out was a
`git show --stat` per candidate commit, which is what made the choice look
close. It is not needed: `_unmerged_commits` already runs one `git log` over
every unmerged ref to read the subjects, and `--name-only` folds the paths
into that same walk. Measured on this repository - 4.6 ms to 8.8 ms over 50
commits, 9.5 ms to 25.1 ms over 200 - against roughly 4 ms of process spawn
*each* for the per-commit form. The subject marker was not taken; nothing
recommended it once the diff read cost a few milliseconds.

The rule is the narrow one this item's evidence supports: a commit whose whole
diff sits inside the configured queue directory stakes no claim. No
frontmatter-versus-body parse, which would in any case have failed on the
capture and triage commits, since both write frontmatter.

**Applied to both reads, not only to `next`.** `branches_in_flight` asks
whether an item is startable and `precedence` asks which of two sessions
yields; a branch that only recorded a note is carrying nothing, so it is a
rival in neither. Split, they would have ordered a live session behind a
commit nobody was working from.

**It fails toward keeping the mark, deliberately.** A merge prints no paths
under `--name-only`, and a path git quoted does not match the prefix; neither
is evidence of annotation, so both keep their claim. An item wrongly left
marked is one a session picks around; an item wrongly unmarked is two sessions
on one piece of work (`PL-PRHN`).

**Measured after the change, on this checkout.** `bin/docket flight` went from
four items to one, and the one is `PL-66FP`, the only branch actually
implementing anything. `PL-3833`, `PL-K1DL` and `PL-P3B6` lost their marks.

**The residual, which is real and was live at the time of writing.** `PL-P3B6`
was being implemented by a session whose only *pushed* commit filed two items
and changed nothing else - a capture by this rule and a live claim in fact.
Three things bound it: a branch named `claude/pl-p3b6-...` would have carried
the claim in its name, which is read whatever the diff says; `list_sessions`
sees a session that has committed nothing at all, which is functionally this
case and is the guard built for it; and the mark returns on the first commit
outside the queue. `.claude/skills/docket/SKILL.md` now says so where it asks
for that first push. Two refinements were tested against the eight false marks
and rejected: "changes only the item file it leads with" misreads a capture and
a `docket record` write, and "creates a new item file" misreads the `docket
record` write while not recovering `PL-P3B6` either.
