---
id: PL-7B3G
title: bin/docket concurrent ranks its batch by priority alone, so a session clearing the gate cannot ask it for N startable gate entries that do not collide
priority: P2
effort: M
status: blocked
classes: infra
feature: parallel-sessions
touches: subprojects/docket
blocked-by: PL-4ZK8
added: 2026-09-07
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

Sequenced behind `PL-4ZK8` (the `concurrent` batch mixes in-flight and
needs-decision work) rather than folded into it, on this item's own reading: if
`PL-4ZK8` is answered by filtering, the startable axis is built and what remains
here is gate membership alone; if it is answered by marking, both axes are still
to build. Either way the shape of this work is decided there, so the edge is
declared in `blocked-by` where `bin/docket next` reads it instead of sitting in
prose - which is the defect `PL-YPWT` recorded against a different item on the
same day.
