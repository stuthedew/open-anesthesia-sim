---
id: PL-N1JK
title: Two sessions triaged PL-X35V and PL-ZVS7 within the hour: a triage pass is structurally invisible to the in-flight guard
priority: P2
effort: M
status: done
classes: defect, infra
feature: parallel-sessions
milestone: v0.4.5
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/README.md, .claude/skills/docket/SKILL.md
added: 2026-09-06
closed: 2026-09-06
pr: 393
verify: uv run pytest subprojects/docket/tests/test_cli.py && grep -q 'def test_triage_names_an_item_whose_file_a_branch_has_already_edited' subprojects/docket/tests/test_cli.py
---

**Problem.** On 2026-09-06 two sessions independently triaged `PL-X35V` and
`PL-ZVS7`. `#386` merged first; `#387` reached the same two answers, hit a
merge conflict on both files, and resolved wholly in favour of `origin/main`.
The second session's work on those two items was discarded at the merge.

The guard did not fail through neglect. The session running `#387` fetched
`origin` and ran `bin/docket show` on all four untriaged ids at 16:59 UTC;
none came back `IN FLIGHT`.

**Why it matters.** The reason is a deliberate rule working exactly as
designed, which is what makes this worth recording rather than fixing on
sight. `PL-X3WZ` established that the in-flight mark is read from what a
commit *changed* as well as from its subject, and that a commit whose whole
diff sits inside `docs/items/` is a capture, a triage pass or a note - not
work - because reading those as work took startable items out of `docket next`
for every session.

A triage pass has, by definition, no diff outside `docs/items/`. So it can
never raise the mark, and two triage passes cannot see each other through
`show`, `next` or `flight` however carefully each one fetches. The documented
cover is the branch name: `claude/pl-k7qx-short-slug` carries the claim
whatever the diff. Both of these sessions were on harness-generated branches,
which the `docket` skill already says have no cover until they commit outside
the queue - and a triage pass never does.

This is `PL-66FP` (two sessions cut v0.3.7 independently) in a different
place: the same collision, on the one class of work whose diff shape puts it
outside every id-matching guard the project has.

**Where.** `subprojects/docket/src/docket/` - whatever computes the in-flight
mark from a branch's diff, and `bin/docket show`, `next` and `flight` which
read it. `.claude/skills/docket/SKILL.md`'s **Mode: triage**, which tells a
session to skip an item marked `IN FLIGHT` without saying that a triage pass
can never carry that mark. `PL-X3WZ` and `PL-66FP` carry the reasoning either
side of this.

**What is not yet decided.** Whether the fix is in the tool or in the
instructions, and it is genuinely open:

- **Tool.** Let a queue-only branch raise a weaker mark that `triage` reads
  and `next` ignores - the two commands want opposite answers from the same
  fact, which is the observation `PL-X3WZ` did not have to make because
  nothing then read the mark for triage.
- **Instructions.** Require a triage pass to name its branch after the ids it
  is triaging, restoring the documented cover for the one case that cannot
  earn it any other way.
- **Neither.** Accept the collision: a duplicated triage pass costs one
  session's queue edits and a conflict that resolves mechanically, which is
  far less than the two-sessions-on-one-item cost `PL-PRHN` weighs. The
  session list is the existing partial answer, and it warned nobody here
  because neither title named the items.

**Done when.** Either the mark distinguishes "a branch is triaging this" from
"a branch is working this", or the `docket` skill's triage mode says plainly
that the in-flight mark cannot fire for a triage pass and names what a session
should do instead - and whichever is chosen, `PL-X3WZ`'s reasoning is amended
rather than contradicted.

**Decided: the tool, on a stronger signal than the option above named.** The
mark now distinguishes the two, but not by asking whether a *branch* is
queue-only - it asks which item *files* a branch's diff has changed.
`FlightReport.editing` names, per item, a ref that has written to
`docs/items/<id>-*.md`, read from the paths `_unmerged_commits` was already
parsing for `_annotates_only` and throwing away.

That is better than the queue-only-branch reading in three ways, and the
difference is that it measures the thing that actually conflicts. It needs no
branch name, so it fires for the harness-named branches both of these sessions
were on. It needs no subject, so a work branch that also captured a finding is
reported against the item it captured rather than only the item it names. And
it is precise to the file, so a triage pass on `PL-X35V` says nothing about a
triage pass on `PL-ZVS7` - a mark that fired on "some branch is editing the
queue" would fire on nearly every branch and be trained out within a week,
which is the retirement test `CLAUDE.md` states.

`PL-X3WZ` is amended rather than contradicted: `ids` still comes from
`branches` alone, so `next`, `list` and `status` go on offering an item whose
file a capture commit touched. The new reading ranks nothing. It prints in the
two places where it changes a decision - `triage`, which is about to write to
that file, and `show`, which is about to start the item - and is deliberately
absent from `flight`, where capture being mandatory would put a row under
nearly every live branch while changing no answer.

The instructions half is done too, because a mark nobody can read is not a fix:
the `docket` skill's **Mode: triage** now names the second line and says to skip
on it, and **Mode: start an item** says the file edit is the weaker cover a
harness-named branch has where the branch name would have been the strong one.
