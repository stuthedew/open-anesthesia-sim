---
id: PL-6TP8
title: PL-6ZQY's verify-meaning cluster has no causing item, so eleven open items each re-decide what a non-zero exit proves and none of them can be marked as a generator
status: untriaged
feature: generator-heads
touches: docs/items
added: 2026-09-17
---

**Problem.** PL-6ZQY's verify-meaning cluster has no causing item, so eleven open items each re-decide what a non-zero exit proves and none of them can be marked as a generator

**Why it matters.** `verify:` was specified as "a command that fails before the
work and passes after" and nothing else about it was written down, so each
consumer - the landed check, the whole-store replay, the delegated audit, the
close-out - reads a different meaning out of one exit code, and a non-zero exit
means both "not started" and "prerequisite broken". Eleven open items each
answer that for themselves.

**Why no existing item can head it.** `PL-LKGL` is the measurement `PL-6ZQY`
cites and it is `done` (#658): it names the root sentence - the field tests for
the presence of the fix, never for the presence of the fault - decided one
facet, and explicitly refused the recorded fault test, so the general contract
was left unwritten. `PL-0M32` is the sharpest sub-question ("can 'finished
under a renamed test' be told from 'not started' at all") and is scoped to that
one ambiguity. `PL-D0K3` is a policy question about ten specific `doc_check`
commands. None of the three settles what an exit code may be read to mean.

**What the head has to decide.** What each consumer may conclude from a
`verify:` command's exit status, and what the field owes beyond a command
string - whether a fault test is recorded beside the fix test, what a consumer
does where the command cannot run at all, and which consumers may decline
rather than answer.

**Candidate members (11, unverified).** `PL-T7VS`, `PL-0M32`, `PL-Q8RQ`,
`PL-6TN8`, `PL-D0K3`, `PL-3DXV`, `PL-6YWK`, `PL-2M4X`, `PL-6YL1`, `PL-Y4YX`,
`PL-H9GV`.

**Done when.** One item poses that decision, carries a `root-cause-of:` naming
the members that survive confirmation, and the members are re-pointed at it or
dropped against it.

**Where this came from.** `PL-6ZQY` found six clusters under one mechanism -
*the apparatus infers a fact it could have recorded* - and `PL-VX5H` built the
way to rank one: `root-cause-of:` on the item that causes the cluster, which
`docket next` then offers above every band but `P0`. Marking the six on
2026-09-17 found that only two have a causing item in the store. `PL-BHVM` and
`PL-L4YG` carry the field now; this cluster is one of the four that has nobody
to carry it, so it stays flat in `P2` exactly as `PL-VX5H` says a generator
does.

**How the membership below was arrived at, and what it is worth.** A 2026-09-17
pass read every open item's front matter, and each candidate's title and one
quoted sentence from its brief. That is enough to say these are plausibly one
problem and **not** enough to write the `root-cause-of:` line: the field is a
recorded fact rather than an inference, which is the whole of why it outranks a
`safety`-classed `P1`. Confirm each against its brief before writing it. This
is `PL-6ZQY`'s own caveat about its map, arriving at the next step.
