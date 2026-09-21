---
id: PL-K13H
title: Recover four items whose only copy is on a branch with no live session: PL-BXNH, PL-HVLJ and PL-7H9Y on claude/festive-allen-nj1x98, PL-3QM9 on claude/cool-pascal-emsw3c
priority: P2
effort: S
status: done
classes: infra
feature: stranded-recovery
milestone: v0.5.0
touches: docs/items
added: 2026-09-21
closed: 2026-09-21
pr: 832
payoff: four captured findings stop existing only on branches nobody is merging, where the default branch cannot see them and no session will be offered them
verify: test -f docs/items/PL-BXNH-recover-the-four-squash-commit-bodies-lost-on.md && test -f docs/items/PL-HVLJ-doc-check-reads-local-tags-so-a-checkout-whose.md && test -f docs/items/PL-7H9Y-pl-kfwl-s-stated-symptom-does-not-reproduce-on.md && test -f docs/items/PL-3QM9-bin-docket-flight-reports-a-branch-s-age-by.md
---

**Problem.** Recover four items whose only copy is on a branch with no live session: PL-BXNH, PL-HVLJ and PL-7H9Y on claude/festive-allen-nj1x98, PL-3QM9 on claude/cool-pascal-emsw3c

**Measured 2026-09-21**, from `bin/docket stranded` cross-checked against the
live session list, which is the read no command in this package can make:

| Branch | Age | Only there | Owning session |
| --- | --- | --- | --- |
| `claude/festive-allen-nj1x98` | 67 min | `PL-BXNH`, `PL-HVLJ`, `PL-7H9Y` | idle, `connection_status: disconnected` since 01:48 |
| `claude/cool-pascal-emsw3c` | 2 h | `PL-3QM9` | none listed |
| `claude/sharp-lamport-t545rs` | 56 min | `PL-X5PK` | live, and working that item |

**Why it matters.** `docket stranded` says the quiet part itself: "A branch on
live work will appear here and that is expected; the hole is a branch nobody
will merge." These two branches are that hole. An item that exists only on an
unmerged branch is invisible to `bin/docket next`, to the session-start digest
and to every debt gate, so the finding is not deferred - it is gone, and nothing
in the store would ever say it had been.

`PL-BXNH` is the sharpest case, because it is itself the recovery of the four
lost squash-commit bodies the digest has been reporting for hours. A recovery
item that is itself stranded is the failure compounding.

**`PL-X5PK` was deliberately left.** Its branch carries a live session whose own
task summary reads "Checking my branch state and whether PL-X5PK is pushed", so
recovering it here would duplicate an item that session is about to push, and
`docket stranded` exists to find abandoned work rather than to race live work.

**Filed before the work, not after.** `CLAUDE.md` requires repository work no
item names - a merge, a stale ref, a docs sweep, a stranded recovery - to be
filed first and worked under its id, because every in-flight guard this project
has matches a `PL-` id and unfiled work reads as nobody's to all of them.

**Approved 2026-09-21** (project owner, ratified), over leaving the branches to
be noticed again by a later `docket stranded`, and over running the two branches
as separate recoveries.

**Done when.** The four briefs stand on the default branch, the store validates,
and the recovered items keep the `untriaged` status they were captured at, so
the next triage pass judges them rather than this recovery doing it blind.

**Closed 2026-09-21.** All four recovered by `git checkout` from the branches
above. `bin/docket check` reports 0 errors and the open count reconciles: 339
before, 343 after - the four recovered, with this item closed and so not open.
Each stays `untriaged`, which is what they were captured at; none is triaged
here, because this item's commission is recovery and banding them is a judgment
the next triage pass owes with the briefs in front of it.

**The first push of this item failed CI, and the cause is worth recording.**
Setting `status: done` without a `verify:` command is a `docket check` error -
a closed item owes the command that proved it. The session missed it by running
`bin/docket check | grep -E "errors"`, which matches the plural summary and not
the singular "1 error", so an empty grep read as a clean store. Read the
command's output rather than filtering it; the count line says "0 errors" only
when there are none or many.
