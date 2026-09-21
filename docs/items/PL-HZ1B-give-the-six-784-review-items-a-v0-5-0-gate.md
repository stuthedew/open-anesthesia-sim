---
id: PL-HZ1B
title: Give the six #784 review items a v0.5.0 gate disposition, the half of their recovery #806 left: untriaged today, each becomes a make check failure the moment triage gives it classes
priority: P2
effort: S
status: done
classes: housekeeping, docs
feature: two-run-attribution
milestone: v0.5.0
added: 2026-09-20
closed: 2026-09-21
pr: 814
payoff: stops a later triage pass re-deriving a gate disposition that #812 already recorded, and takes the six items off the prerequisite list PL-NQKP's pass was routed around
verify: grep -q '^### Declined to Gate 2, because this milestone' ROADMAP.md
---

**Problem.** Recover the seven items stranded on claude/vigilant-albattani-3lkcb3 and give each a v0.5.0 gate disposition, since a triaged safety item with none fails make check

**Decided by the project owner 2026-09-20, ratified** - chosen over working
`PL-4KZD` alone and over leaving the three attribution defects as separate
items: the marks-panel attribution defect is worked as **one problem** under
`feature: two-run-attribution`, with **`PL-LHBY` as the carrier and `PL-4KZD`
folded into it**. `PL-LHBY` was preferred because it reproduces offscreen
against the merged tree and its `touches` reach `app/qt_widgets.py`, which
`PL-4KZD`'s does not.

**The recovery half landed 2026-09-20 as `#806`, and the gate half did not.**
All seven files are on `main`, and `PL-LHBY` - the carrier - was admitted to
v0.5.0's frozen list under its own heading, "Added 2026-09-20 under the
unconditional safety/science exception - 1 entry". The gate reads 181 entries,
3 open: `PL-LHBY`, `PL-4KZD`, and `PL-WZVZ` blocked outside it. **What `#806`
did not do is disposition the other six** - `PL-25DD`, `PL-624C`, `PL-FKN7`,
`PL-R17Y`, `PL-RS3Z`, `PL-WG73` - and that is the whole of what is left here.

**It is not failing `make check` today, and that is the trap.**
`doc_check`'s gate check fires only on a *triaged* debt item, and all six are
`untriaged`, so they carry no `classes` and nothing can yet say whether they
are debt. The failure arrives with triage, not with the items. `PL-NQKP`
(triage the 35 untriaged captures) is live on
`origin/claude/blissful-mendel-ccad0y` and routes these six here by name -
"work the 29 here and leave the 6 to `PL-HZ1B`", because a gate scoping
decision does not belong inside a field-filling pass. So this item is a
**prerequisite of that triage**, and doing them in the other order reddens
`main`.

**Original framing, kept because the reasoning still applies to the six.**
Seven item files existed only on
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

**Done when.** Each of `PL-25DD`, `PL-624C`, `PL-FKN7`, `PL-R17Y`, `PL-RS3Z`
and `PL-WG73` has a v0.5.0 disposition recorded in `ROADMAP.md` - on the frozen
list where it is debt under the presence rule or the safety/science exception,
or in a `### Declined to Gate ...` subsection saying why - with the group
heading's count moved to match, since `tools/doc_check.py` holds those numbers
to the list. `make check` green, and `PL-NQKP`'s triage pass is then free to
run without reddening `main`.

Already done and not to be redone: the recovery itself, `PL-LHBY`'s frozen-list
entry, and `PL-4KZD`'s record of the fold - all on `main` as of `#806` and
`#805`.

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

**Closed 2026-09-21 by `#812`, which did both halves in one commit.** The
sequencing worry above did not materialise, and the reason is worth recording:
`#812` triaged the six *and* wrote their gate dispositions in the same commit,
so `main` was never red between the two. `PL-NQKP`'s pass merged as `#810`
minutes earlier, having correctly left the six alone.

What `#812` recorded, against the `**Done when.**` above:

- `PL-25DD` is `defect, safety, ux`, so it re-enters unconditionally and is on
  the frozen list under "Added 2026-09-21 under the unconditional safety/science
  exception - 1 entry". The list moved 181 to 182 and the timeline row with it.
- `PL-WG73` (`defect, ux`) and `PL-624C` (`defect, test`) are debt but not
  `safety`, so the presence test applies and answers no - `git log -S` dates
  both symbols to `d048aca`, the pull request that built the fork control.
  Both are in a new `### Declined to Gate 2, because this milestone's own work
  created them - 2 entries`.
- `PL-FKN7`, `PL-R17Y` and `PL-RS3Z` are classed `test` alone. `test` is not in
  `docket.toml`'s `debt_classes`, so the gate is owed no disposition for them,
  which is why only three of the six appear above. `doc_check` reporting 0
  errors on the merged tree is what says so rather than this sentence.

`make check` green on `5bdd1a8e`.
