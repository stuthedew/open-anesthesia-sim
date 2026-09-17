---
id: PL-XF2Y
title: PL-C4RS's verify: command has started passing on main, the third instance of a non-discriminating sentinel redding main and the second in one day, so PL-879R's decision is now the thing holding main red
status: untriaged
feature: sentinel-verify-commands
added: 2026-09-16
---

**Problem.** PL-C4RS's verify: command has started passing on main, the third instance of a non-discriminating sentinel redding main and the second in one day, so PL-879R's decision is now the thing holding main red

**Found while closing `PL-D1RT`** (the stale `v0.5.x — the interface pass`
citations) in `#643`, on the scheduled re-check of that pull request.

**The failure, verbatim** from run 2126 on `4167e2a` (2026-09-16 20:05:10Z):

> `PL-C4RS`, `PL-D1RT` are open but their `verify:` command already passes (2
> of 166 checked).

`PL-C4RS` (Gate 1's group headings and v0.5.0's `Required scope` disagree on
three ids) carries `! grep -q 'Nineteen items, in the order the dependencies
allow' ROADMAP.md`. `#640` (`PL-83LS`, `PL-R7XK`) moved `PL-MN4J` into
v0.5.0's `Required scope` and recorded that it "reads **twenty** items", which
deleted the phrase. Nothing about `PL-C4RS`'s own problem was touched.

**Measured, not predicted.** `bin/docket check --verify` on `#643`'s head
merged with `4167e2a`, in a scratch worktree: **1 error, `PL-C4RS`**, 165
commands in 177.2s. So `#643` removes `PL-D1RT`'s error and regresses nothing,
and `main` stays red on `PL-C4RS` alone.

**Why this is the class rather than the instance.** Three now, and the pattern
is identical each time - a sentinel that names something *another* item's work
can satisfy, so it flips from failing to passing with no one touching the item
it guards, and `main` goes red where no pull request can see it:

| Instance | Sentinel | What satisfied it |
| --- | --- | --- |
| `PL-Y1W6` (dropped) | `PL-S5YM`'s bare `-k` selector | a braced-citation test `#593` added |
| `PL-D1RT` | `! grep` for a timeline row | `#634` renumbered the row |
| `PL-C4RS` | `! grep` for "Nineteen items…" | `#640` made it twenty |

Two of the three landed on 2026-09-16, which is the rate that makes this worth
raising rather than filing. It meets `CLAUDE.md`'s compounding-friction tests
on two counts: the check **gives a wrong answer silently** - `docket verify`
would `ACCEPT` a branch that did none of the item's work - and it **sits
upstream of everything**, in the gate every merge to `main` runs.

**`PL-879R` is the fix and it is not this item.** That item - `docket check`
advises on a `verify:` command's *outcome* but never its *shape* - is
`needs-decision` and carries `feature: dev-tooling`, a standing theme rather
than a group with a "done when". **It belongs in this feature**, and whoever
takes it should move it here; it was left where it is because this was found on
a hotfix branch deliberately kept to one item file.

**Not fixed here, and `PL-C4RS` was deliberately not touched.** `bin/docket
show PL-C4RS` reports its file already edited on
`origin/claude/awesome-heisenberg-gp7ev6` (last commit 2026-09-16), and its
remedy needs the same clause-by-clause reading `PL-D1RT` got - whether the work
is genuinely done or the `grep` merely flipped - against `ROADMAP.md`, which 26
open items declare.

**Done when** `main` is green, which needs `PL-C4RS` disposed of the way
`PL-D1RT` was, and `PL-879R` answered so that the fourth instance is caught
when the command is *written* rather than when it starts passing.

**Superseded in part, 2026-09-16, by `#645`** (`PL-D1RT`, `PL-KND7`: take main
green). That branch closes `PL-D1RT` *and* re-points `PL-C4RS`'s sentinel to
pin a sentence the correction must add rather than an absence, leaving the item
open because its work is genuinely outstanding - which is the error's other
disposition and the right one for it. It reports `bin/docket check --verify`
at **0 errors** on its tree merged with `4167e2a`.

So the two paragraphs above about `PL-C4RS` being unfixed describe the state on
2026-09-16 at 21:06Z and not the state once `#645` lands.

**What is not superseded is the whole of the point.** Three instances, two of
them in one day, and `#645` took *opposite* dispositions on two of them from
one defect - one closed because its work had landed, one re-pointed because its
work had not. That the same fault yields opposite remedies is the evidence that
the fault is the **sentinel's shape** rather than any item's state, which is
`PL-879R`'s subject and still undecided.
