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

**One measurement to pass to `PL-8JQQ`, from the other side of it.** That item
is the implementing session's own record of the same events, and this is the
half it could not see. `PL-8JQQ` reports `flight` silent on branch head
`6b2008c8`; it later reported the branch correctly on head `d9f81cc4`. What
changed between the two is not time and not a fetch:

- At `6b2008c8` the branch carried **three** commits absent from `main` -
  `b94ba164` and `78c8336c`, whose *content* had landed as `#801`'s squash
  `1531a8bc` but whose commit objects had not, plus the implementation commit.
  `flight` was silent.
- The branch was then restarted from `origin/main` and the implementation
  cherry-picked onto it, so it carried **one** commit absent from `main`.
  `flight` reported `PL-3K9B claude/lucid-dijkstra-i1qy6x last commit today`
  immediately, with no other change.

So the trigger looks like a branch carrying already-squash-merged commits
*alongside* the new one, rather than a squash from the branch having happened
at all - which is a narrower and more testable claim than "goes blind after a
squash-merge", and it points at how the commit range `flight` parses is
chosen rather than at ref staleness. Offered as a lead; `PL-8JQQ` is the item
and its session is live on it.
