---
id: PL-HZ1B
title: Recover the seven items stranded on claude/vigilant-albattani-3lkcb3 and give each a v0.5.0 gate disposition, since a triaged safety item with none fails make check
status: untriaged
feature: two-run-attribution
added: 2026-09-20
---

**Problem.** Recover the seven items stranded on claude/vigilant-albattani-3lkcb3 and give each a v0.5.0 gate disposition, since a triaged safety item with none fails make check

**Decided by the project owner 2026-09-20, ratified** - chosen over working
`PL-4KZD` alone and over leaving the three attribution defects as separate
items: the marks-panel attribution defect is worked as **one problem** under
`feature: two-run-attribution`, with **`PL-LHBY` as the carrier and `PL-4KZD`
folded into it**. `PL-LHBY` was preferred because it reproduces offscreen
against the merged tree and its `touches` reach `app/qt_widgets.py`, which
`PL-4KZD`'s does not.

**What is stranded, and why it matters.** Seven item files exist only on
`origin/claude/vigilant-albattani-3lkcb3`, filed there by the adversarial
review of `#784`. They are not in the default branch's store, so
`bin/docket next` cannot see them and a session picking up the marks-panel
defect works `PL-4KZD` alone and re-derives what `PL-LHBY` already measured:

- `PL-LHBY` - a branch halted on a learner's mark reports nothing, because the
  marks panel draws standings from the reference run only. `P1`, `M`,
  `defect, safety`, already carries `feature: two-run-attribution`.
- `PL-25DD` - the wash-in state line and the off-scale notice sit in the shared
  chart column with no run attribution once a branch is drawn. The third of the
  same family.
- `PL-8JQQ`, `PL-624C`, `PL-FKN7`, `PL-R17Y`, `PL-RS3Z`, `PL-WG73` - the rest of
  that review's findings.

`bin/docket stranded` prints the recovery recipe per file.

**The gate is the part that needs care, and it is why this is an item rather
than a `git checkout`.** `tools/doc_check.py` fails `make check` on any
*triaged* debt item that v0.5.0's gate records no disposition for - neither on
the frozen list nor in a `### Declined to Gate ...` subsection. Recovering a
`ready`, `safety`-classed item into the store therefore reddens `main` until
`ROADMAP.md` carries its disposition. `PL-3K9B` hit exactly this on
2026-09-20: `PL-4KZD` was triaged on a branch and the branch went red until
the gate entry was written (`#801`, then `#805`).

So: recover, then disposition each recovered debt item in the same commit.
`PL-LHBY` is `safety`-classed and re-enters the gate under the same
unconditional exception `PL-3K9B` and `PL-4KZD` entered under, so it belongs on
the frozen list rather than declined.

**Folding `PL-4KZD` is a gate change, not only a queue change.** `PL-4KZD` is
currently the one open v0.5.0 gate entry a session can clear (178 of 180
cleared). Dropping it as superseded without putting `PL-LHBY` on the gate would
leave the gate reading clear while the defect it stands for is still open,
which is the bookkeeping drift `gate-list-integrity` (`PL-0VFF` and its five
siblings) was closed to stop. Do both in one commit or neither.

**Done when.** The seven files are in the default branch's store; every
recovered debt item has a v0.5.0 gate disposition; `PL-LHBY` is on the frozen
list and `PL-4KZD` records the fold against it; `make check` is green; and
`bin/docket stranded` reports nothing on that branch.

**One finding to pass on, not to act on here.** `PL-8JQQ` claims
`bin/docket flight` goes blind to a branch once an earlier pull request from it
squash-merged, and names `PL-3K9B`'s implementation as the instance. This
session observed the opposite - after the restarted branch was pushed, `flight`
did report `PL-3K9B claude/lucid-dijkstra-i1qy6x last commit today`. Not
adjudicated here; whoever picks `PL-8JQQ` up should know the claim is at least
not universal.
