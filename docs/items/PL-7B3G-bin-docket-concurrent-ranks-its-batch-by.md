---
id: PL-7B3G
title: bin/docket concurrent ranks its batch by priority alone, so a session clearing the gate cannot ask it for N startable gate entries that do not collide
priority: P2
effort: S
status: ready
classes: infra
feature: parallel-sessions
touches: subprojects/docket, .claude/skills/docket/modes/picking.md
added: 2026-09-07
verify: grep -q 'def test_concurrent_can_draw_the_batch_from_the_current_step_alone' subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket concurrent ranks its batch by priority alone, so a session clearing the gate cannot ask it for N startable gate entries that do not collide

**What was observed.** Picking four gate entries to start as parallel sessions
on 2026-09-07 needed three facts at once: on the frozen gate under v0.5.0,
`status: ready`, and no shared file with the others chosen. `bin/docket wave`
gives the first as a bare id list, `bin/docket list` the second, and
`bin/docket concurrent` the third — and none of the three takes the others as
an argument, so the pick was made by parsing every open gate entry's front
matter in a throwaway script.

**Why it matters.** `CLAUDE.md` says to find the decidable part and put it in
code, and all three of those facts are decidable from the store. The beat this
project is on is *clear the gate*, and the fan-out that clears it fastest is
the one that asks for N non-colliding startable entries — a question the
tooling cannot currently be asked, so every fan-out re-derives it at full
session cost.

**Shape of the fix, not decided.** A `--gate` filter and a `--startable`
filter on `concurrent`, or a first-class `bin/docket fanout <n>`. Note this
overlaps `PL-4ZK8` (`concurrent`'s batch mixes in-flight and needs-decision
work): if that one is fixed by filtering rather than marking, this becomes the
gate-membership axis alone and shrinks. Triage may reasonably fold the two.
## Triaged 2026-09-13

[superseded 2026-10-03] Sequenced behind `PL-4ZK8` (the `concurrent` batch mixes in-flight and
needs-decision work) rather than folded into it, on this item's own reading: if
`PL-4ZK8` is answered by filtering, the startable axis is built and what remains
here is gate membership alone; if it is answered by marking, both axes are still
to build. Either way the shape of this work is decided there, so the edge is
declared in `blocked-by` where `bin/docket next` reads it instead of sitting in
prose - which is the defect `PL-YPWT` recorded against a different item on the
same day.

## Re-triaged 2026-10-03

**`PL-4ZK8` was answered by filtering (#1299), so the startable axis is built
and gate membership is the axis left.** The bare batch is now drawn from
`plan.offerable` - what `next` ranks - and names the decisions and the work in
flight beneath it. The shape this brief left open is settled as a flag on
`concurrent` rather than a `bin/docket fanout` command: the batch, its
`--limit` fill and the two lines beneath already live in `cmd_concurrent`, and a
second command would duplicate them. Effort moves from `M` to `S`, the shrink
this brief predicted. Nothing else holds it: what the current step's scope is
comes from `Scope.placement`, which `next` already reads, and no open item
carries `generator: live`. Reproduced 2026-10-03: `bin/docket concurrent
--help` offers `item` and `--limit` and nothing that narrows the batch by scope
or gate.

**Done when.** `bin/docket concurrent` takes a flag that draws the bare batch
only from the work `Scope.placement` puts in the current step's scope - the
gate's open entries while a gate is being cleared - after `plan.offerable`, so
the startable rule is not rebuilt. `--limit N` fills out from the same
population, and the decisions and in-flight lines beneath are unchanged. Where
no plan or scope can be read, the flag says so and offers nothing rather than
the whole queue. A test in `subprojects/docket/tests/test_cli.py` pins a
startable in-scope item present and a startable out-of-scope item absent.
