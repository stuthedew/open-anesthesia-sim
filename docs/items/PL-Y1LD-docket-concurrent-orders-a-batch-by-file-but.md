---
id: PL-Y1LD
title: docket concurrent orders a batch by file, but the lane mechanism separates only two sessions, so the third and fourth simultaneous session have no command that picks for them
priority: P3
effort: M
status: done
classes: session-cost, infra
feature: parallel-sessions
milestone: v0.5.17
touches: docs/items
added: 2026-09-06
closed: 2026-09-27
pr: 1202
verify: grep -qF 'Answered 2026-09-27: Q1 ratified' docs/items/PL-Y1LD-docket-concurrent-orders-a-batch-by-file-but.md
---

**Problem.** docket concurrent orders a batch by file, but the lane mechanism separates only two sessions, so the third and fourth simultaneous session have no command that picks for them

**Observed 2026-09-06**, handing out four gate items to four simultaneous
sessions. `docket.toml`'s own comment says "Two lanes and no more, because two
sessions can hold a repository between them and four cannot", and that is
right about lanes - but the project owner ran four anyway, and the apparatus
had no answer for sessions three and four.

What exists: `bin/docket next <lane>` picks for two sessions, and `bin/docket
concurrent` prints a file-disjoint batch. What is missing is the join between
them. `concurrent` returned a 29-item batch, but choosing four from it that
were each startable, on the gate, worth doing, and pairwise disjoint was done
by hand - reading `touches` for ten candidates and cross-checking them in a
scratch script. That is the work `next` does for one session and no command
does for four.

**The shape a fix probably takes**, though this is a design round rather than
a decided approach: `bin/docket concurrent --pick <n>` returning the best `n`
mutually disjoint startable items in rank order, which is `next`'s ranking
applied to `concurrent`'s graph. That is one command, reuses both halves, and
is the deterministic-tooling answer to a judgment a session currently re-makes
at full context every time.

**Where.** `subprojects/docket/src/docket/cli.py` - `cmd_concurrent` and the
ranking `cmd_next` applies, which are the two halves that would be joined.

**Done when.** Either one command returns the best `n` mutually disjoint
startable items in rank order, so a session handing out work to three or four
sessions runs a command rather than a scratch script, or the project records
that four-way work is rare enough to keep doing by hand and why.

**Why it matters, and why it is not urgent: it does not meet the
compounding-friction bar.** Nothing
gives a wrong answer silently, nothing is being routed around, and the manual
pass took one session a few minutes. It is worth doing when four-way work
becomes routine rather than a one-off.

**Decision needed.** Is the join between `next`'s ranking and `concurrent`'s
graph worth building - `bin/docket concurrent --pick <n>`, returning the best
`n` mutually disjoint startable items in rank order - or is four-way work rare
enough to keep doing by hand? Nothing gives a wrong answer today and the manual
pass took one session a few minutes, so this is a question about how routine
three- and four-way sessions become.

## Design round 2026-09-27: recommendations

**Re-confirmed against the tree, 2026-09-27.** The two halves are still
unjoined: `cli.cmd_next` ranks through `plan.recommend`, `cli.cmd_concurrent`
orders through `concurrency.parallel_batch`, and no command returns `n`
mutually disjoint startable items. The `docket.toml` sentence the brief
quotes ("Two lanes and no more, because two sessions can hold a repository
between them and four cannot") is gone; the comment now reads "Two
simultaneous sessions then never rank onto the same item", and the lane
mechanism still places work on one of two sides. So the mechanism is as the
brief describes it; what has moved is the premise.

**The brief's own trigger has fired, and not in the way it expected.** It made
this "worth doing when four-way work becomes routine rather than a one-off".
Under the Projects trial (`PL-NZC0`, project owner, 2026-09-25, ratified),
three-, four- and five-way work is the routine: at 19:54 UTC today `bin/docket
flight` showed four branches with open pull requests (#1197, #1198, #1199,
#1200) and this thread beside them; the v0.6.0 project's own thread list, read
at 20:01 UTC, showed 23 threads started on 2026-09-27, four of them within
eleven minutes at 05:10-05:21 UTC; and that project's instructions cap two
code threads and three design threads at once. None of those sessions was
picked the way the brief imagined, and none could be. The owner picks
*features* into an Order list; the coordinator runs each as a chain, one item
at a time, from `bin/docket feature` and the `blocked-by` waves; the two code
slots hold one product chain and one workflow chain, which share no files
(`ROADMAP.md` § "Debt gate: the frozen list"); and `bin/docket concurrent` is
run on the chain's next item before each thread starts, as the shared-file
check. A `--pick` ranks across the whole queue by band and hands out whatever
wins, which is the one thing that project's instructions forbid the
coordinator: it starts threads for nothing the owner has not picked. The join
would have no caller. `PL-NZC0` records why the trial runs serial chains
under one coordinator rather than `n` independent sessions - the coordination
evidence it cites - so a fan-out of `n` items picked by rank is the working
shape the project chose against, not one it has yet to reach.

**Q1. Build `bin/docket concurrent --pick`, or record why four-way work is
picked by hand?**
**Recommendation: do not build it, and close this item on the record, with
the premise corrected: four-way work is routine, and it is picked by feature
under the owner's Order and dispatched one chain at a time, so the
rank-ordered join has no caller.** That is the Done-when's second ending,
with "rare" replaced by what was measured. `CLAUDE.md` § "Prefer
deterministic tooling over repeated model work" gates a mechanism on whether
it will genuinely run again and answers no where the benefit is unclear, and
a command nobody calls is the check "that fires every run without changing a
decision" one paragraph later, retired before it is built. Nothing is
downstream of not building it (`.claude/rules/expert-review.md` § "Count what
undoing it would cost, before taking the cheaper route"): if the trial ends
and a session again hands out four items by hand, the need is refiled at the
cost of one `bin/docket new`, in the shape then observed rather than this one,
and the `M` is spent then at the same price as now. The record goes here and
not in `ROADMAP.md` § "Planned milestones": it is a contingency, not a feature
wanted.

*Refused: build it now, as `M` work that reuses two halves already written.*
Cheap to write, and wrong on the gate: it would sit in `bin/docket --help`
unrun, and its tests and README paragraph would be maintained by every session
that touches `cli.py`. "The deterministic-tooling answer to a judgment a
session currently re-makes at full context every time" is the right argument
for a judgment that recurs; this one stopped recurring on 2026-09-25.

*Refused: leave it open until the trial ends.* An open `needs-decision` item
is gate debt (`bin/docket gate` counts it), holds Gate 2 open for a
hypothetical, and is the queue entry that cannot be worked, where every
session reads past it (`CLAUDE.md` § "The queue, and how the project owner
works", capture by readiness). The trial has no end date to block on.

**How, on the owner's answer.** No build thread: this design thread records
the answer as `## Answers 2026-09-27`, sets `status: done` with
`closed: 2026-09-27` and records its own pull request with `bin/docket record`,
since the record is the whole deliverable, and acts on whatever `bin/docket
set` prints about `verify:` at close. [superseded 2026-09-27: `touches:` was re-pointed at `docs/items` at the
close, the only tree this closure changes, so the `verify:` grep reads a
declared path.] Nothing in `cli.py` moves.

**What this settles beside it.** The coordinator's collision check stays
`bin/docket concurrent` on each chain's next item, and `PL-4ZK8`'s
recommendation - the bare batch offers startable work only - is what makes the
bare form pasteable on the day a hand fan-out returns. `PL-7B3G` (N startable
gate entries that do not collide) is the same need at gate altitude and is
sequenced behind `PL-4ZK8`, not this item.

## Answers 2026-09-27

**Answered 2026-09-27: Q1 ratified** (project owner, 2026-09-27, ratified,
over building `bin/docket concurrent --pick`, the join between `next`'s
ranking and `concurrent`'s graph). Not built. The record § "Design round
2026-09-27: recommendations" carries is this item's second Done-when ending
with its premise corrected: four-way work is routine under the Projects
trial, is picked by feature under the owner's Order and dispatched one chain
at a time, with `bin/docket concurrent` on each chain's next item as the
collision check, so the rank-ordered join has no caller. If the trial ends
and a session again hands out several items by hand, the need is refiled in
the shape then observed. Closed on this record in the design round's own pull
request, with no build thread.
