---
id: PL-7790
title: A session that starts an item by pushing only queue-file edits stakes no claim docket next can see
priority: P3
effort: M
status: done
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md, .claude/skills/docket/SKILL.md
added: 2026-09-05
closed: 2026-09-14
pr: 558
verify: uv run pytest subprojects/docket/tests/test_vcs.py -q -k 'deliverable or promoted or resurrect' && grep -q '_queue_only_work' subprojects/docket/src/docket/vcs.py
---

**Problem.** `PL-X3WZ` made the in-flight mark read a commit's diff as well as
its subject: a commit whose whole diff sits inside `docs/items/` stakes no
claim, because captures, triage passes, `docket record` writes and notes
written into a brief all lead with an id they are not implementing. The
residual is the opposite case - a session that genuinely *starts* an item by
pushing only a `touches` fill or a `verify:` command, which is annotation by
the diff and a claim in fact.

**Observed 2026-09-05, live, in the session that made the change.**
`origin/claude/docket-project-check-optimization-da5xn8` carried one pushed
commit, "PL-P3B6, PL-K1DL: file the verify-replay cost, and the rejected path
split", changing two item files and nothing else. The session was implementing
`PL-P3B6` at that moment; its implementation was unpushed. Before the change
that branch marked both ids, and only one of them was real - which is the
defect `PL-X3WZ` fixed - but the mark it lost on `PL-P3B6` was a true signal.

**Why it matters.** It is the direction that costs more of the two: an item
wrongly left marked is one a session picks around, while an item wrongly
unmarked is two sessions on one piece of work (`PL-PRHN`).

**What already bounds it, and why this is not urgent.** Three things, and the
change was taken knowing them:

- A branch named `claude/pl-p3b6-short-slug` carries the claim in its own name,
  which is read whatever the diff says. `.claude/skills/docket/SKILL.md` now
  says so where it asks for the first push.
- `list_sessions` sees a session that has committed nothing at all, which is
  functionally this case, and the skill's start procedure already reads it.
- The mark returns on the first commit outside the queue, which is usually
  minutes away.

**Two refinements were tested against `PL-X3WZ`'s eight false marks and
rejected.** "Changes only the item file whose id leads the subject" misreads
both a single-file capture and a `docket record` write; "creates a new item
file" misreads the `docket record` write *and* would not have recovered
`PL-P3B6`, whose capture commit created both files. Anything that recovers this
case has to read something other than the paths.

**Where.** `subprojects/docket/src/docket/vcs.py` - `_annotates_only` and the
walk that calls it; `.claude/skills/docket/SKILL.md` if the guidance changes.

**Done when.** Either a reading exists that separates "filed this item" from
"started this item" without reintroducing the false marks, or the case is
measured over enough sessions to say the branch-name and `list_sessions` cover
is sufficient and this is closed as accepted.

**Decision needed.** Whether to keep looking for a reading that separates
"filed this item" from "started this item", or to accept the branch-name and
`list_sessions` cover and close this as understood. Both refinements tried
against `PL-X3WZ`'s eight false marks reintroduced them, so anything that
recovers this case has to read something other than the paths - which is the
work, and is why the question is worth answering before it is started rather
than during.

## Worked 2026-09-14: keep looking - and the reading is the item's `touches`, not the commit's paths

**Decided: keep looking, and found it. Built in the same session.** The brief
set the bar itself - "anything that recovers this case has to read something
other than the paths" - and the something is the item's own declared `touches`,
read from the default branch.

**The rule.** A commit whose whole diff sits in `docs/items/` stakes a claim for
id X when X's copy **on the base** declares `touches` that never leaves the
queue directory. `_annotates_only` is untouched: it still answers "did this
commit reach past the queue", which is a fact about the commit, and the new
`_queue_only_work` answers "does this item live in the queue", which is a fact
about the item. Reading both in one place is why the two path-level refinements
failed.

**Tested against `PL-X3WZ`'s eight false marks, which is the bar this had to
clear.** Not one of `PL-HKF4`, `PL-PGZK`, `PL-5WFS`, `PL-22Z3`, `PL-WW08`,
`PL-PMT7`, `PL-55JM`, `PL-N5WZ` declares `touches` inside the queue alone -
`PL-5WFS` comes closest with `plan.py, docs/items/`, and the test is *entirely*
inside, not *mentions*. So the fix costs back none of the eight, with no
path-level help at all. 61 of 920 items declare a queue-only `touches`, about
twenty of them open: the tag items, the triage items, the recovery items.

**A capture is excluded for free, and that is why the base is the tree read.**
A capture creates the item file, so the base holds no copy to declare anything
and the id is dropped rather than marked. No second clause was needed - the
choice of tree is the clause. `_closed_on_base` is then asked again over the
promoted set, because it ran before any of them existed and a `docket record`
write onto a shipped tag item is exactly this shape (`PL-6BDX`).

## Two measurements, and both changed the answer

**The branch-name cover is not a cover.** The brief's first bound was "a branch
named `claude/pl-k7qx-short-slug` carries the claim in its own name". Measured
across every unlanded ref on the remote on 2026-09-14: **none of the eleven
carried an id in its name.** Every branch this project works on is generated by
the web harness before the session starts, and `CLAUDE.md` says such a branch
cannot be renamed. So the first of the three bounds is, in this repository,
structurally unavailable — which is now said in the `docket` skill where it asks
for that first push, alongside the advice to push the failing test instead.

**The third bound fails hardest on exactly these items.** "The mark returns on
the first commit outside the queue, which is usually minutes away" - but an item
whose whole deliverable is a queue edit never makes a commit outside the queue,
so for that class the mark never returns at all. That is the sharp case, and the
brief did not have it.

**And there was a live instance while this was being decided.**
`origin/claude/loving-ride-mo6njm` held one commit, "PL-XR8K: close the v0.4.22
tag item", whose whole diff was `docs/items/`, on a harness-named branch, for an
item whose `touches` is `docs/items/`. `bin/docket flight` reported only
`PL-JRS3`. This session found the other session's work through `list_sessions`,
which `.claude/rules/instruction-writing.md` says warns and never certifies.
After the change, `flight` names `PL-XR8K` on that branch. It was not
constructed as a test case; it was the state of the repository.

**What is left, stated rather than implied.** A session filling in the
`touches` of an item whose work is elsewhere still stakes no claim until its
first commit outside the queue. That residual is real and is the smaller half:
the item that cannot self-heal is the one now covered, and the one that can is
the one left. `bin/docket show` still prints the file edit underneath, which is
the weaker warning `PL-N1JK` added.

**Five tests**, each a defect the absence would let through: the queue-only item
is promoted and leaves `editing` rather than being reported twice; an annotated
item whose work is code is not; an item reaching code *and* the queue is not;
a capture creating the file is not; a write onto a shipped queue-only item does
not resurrect it.
