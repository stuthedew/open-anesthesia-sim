---
id: PL-3ZZT
title: PL-8M8H would move a reading PL-XLQ5 and PL-Y31G document as wrong onto docket branch's restart path, inverting a noisy error into one that destroys a branch with an open pull request
priority: P2
effort: S
status: done
classes: defect, docs
feature: parallel-sessions
touches: docs/items
added: 2026-09-12
closed: 2026-09-12
pr: 500
verify: python3 tools/doc_check.py check && grep -qF 'Decision needed, part two' docs/items/PL-8M8H-docket-branch-tells-a-session-whose-pull.md
---

**Problem.** PL-8M8H would move a reading PL-XLQ5 and PL-Y31G document as wrong onto docket branch's restart path, inverting a noisy error into one that destroys a branch with an open pull request

**Found 2026-09-12** by the full-effort pass over the ref-lifecycle cluster
(`PL-BHVM`), by its completeness critic rather than by any of the twenty
per-item reads - the relation sits in `PL-8M8H`'s prose and nowhere in
`PL-XLQ5`'s or `PL-Y31G`'s, which is exactly why twenty independent readers all
missed it.

**The reading.** `PL-8M8H`'s brief asserts: *"A branch whose landed side is
non-empty has had work taken by a pull request, whatever its commit counts
say."* That is `_landing_split` **unqualified**. It does not carry
`_commits_by_landing`'s narrowing at
`subprojects/docket/src/docket/vcs.py:2801` - `elif all(path in landed for path
in touched): took_one_whole = True` - which is the guard `PL-JHJ3` and `PL-5TRV`
added precisely because `orphaned` fired falsely on its first live run.

**Why that matters more here than where it is today.** Two documented
false-positive shapes both satisfy "landed side non-empty":

- `PL-Y31G` - a branch forked before a history rewrite, whose pre-rewrite blobs
  are duplicated on the base, with nothing merged.
- `PL-XLQ5` - the base holds a superset of the branch's blobs.

Today those cost a spurious line in `bin/docket stranded`. Under `PL-8M8H` the
same reading would drive `bin/docket branch`'s **restart** arm, telling a
session on a branch with an *open* pull request to run the three commands
`.claude/skills/docket/SKILL.md:216` describes as "These three commands destroy
a branch." **The error direction inverts from noisy to lossy**, which is the
distinction `CLAUDE.md`'s safety standard draws between an obvious failure and a
plausible wrong answer.

**Sequencing makes it worse rather than better.** `PL-8M8H` is an open gate
entry at `needs-decision`; `PL-XLQ5` is an open gate entry; `PL-Y31G` sits in
the declined-to-Gate-2 block, so it will not be worked before Gate 2. Nothing in
the ordering forces the qualified reading to be settled first.

**Approach.** Not a `blocked-by` edge - the fix is one addition to `PL-8M8H`'s
own **Decision needed.**, requiring it to answer *which* reading of the split it
adopts, qualified or not, and naming `PL-XLQ5` and `PL-Y31G` as the shapes any
unqualified reading admits. That is done in this item's work, not deferred.

**Done when.** `PL-8M8H`'s **Decision needed.** asks which `_landing_split`
reading it adopts and cites both false-positive items, so the destructive
variant cannot be chosen without the choice being visible.

**Done 2026-09-12.** `PL-8M8H`'s **Decision needed.** is now in two parts, with
the reading question stated as gating the state question, and both
false-positive items named in it. The destructive variant can still be chosen -
that is the owner's call - but it can no longer be chosen without the choice
being visible in the item that makes it.

