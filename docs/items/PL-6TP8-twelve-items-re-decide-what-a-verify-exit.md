---
id: PL-6TP8
title: Twelve items re-decide what a verify: exit status proves, because the field was specified as a command string and nothing else: one contract rather than twelve patches
priority: P2
effort: M
status: needs-decision
classes: defect, infra
feature: generator-heads
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/checks.py, .claude/skills/docket/SKILL.md, docs/items
added: 2026-09-17
root-cause-of: PL-T7VS, PL-0M32, PL-Q8RQ, PL-6TN8, PL-D0K3, PL-3DXV, PL-6YWK, PL-2M4X, PL-6YL1, PL-Y4YX, PL-H9GV, PL-LBW5
---

**Problem.** `verify:` was specified as "a command that fails before the work
and passes after" and nothing else about it was written down. Every consumer -
`docket check --verify`'s landed sweep, the whole-store replay on `main`, the
delegated audit, the close-out - therefore reads its own meaning out of one
exit code, and a non-zero exit means all of "not started", "prerequisite
broken", "selected nothing", "timed out" and "finished under another name".
Twelve open items each answer some part of that for themselves.

**Why it matters.** The mechanism is the one `PL-6ZQY`'s map named under 47% of
the workflow lane: *the apparatus infers a fact it could have recorded.* What a
command's exit status is allowed to prove is a fact the field could carry and
does not, so each consumer infers it, each inference fails in a new way, each
failure is found singly, and each becomes its own item. Patching one closes an
item and leaves the generator standing - `PL-T7VS` (a red `doc_check` voids the
replay for the 29 items gated behind it) and `PL-6YWK` (a command killed at the
120 s limit claims nothing on any run) are the same sentence about two
different consumers.

It is not only queue churn. `bin/docket verify` accepts a delegated branch on a
command that cannot discriminate (`PL-D0K3`, ten `doc_check.py check`
commands), and `bin/docket delegable` hands a cheaper model a commission whose
command proves the wrong tree (`PL-2M4X`). Both are a check passing while the
guarantee it stands for is void, which is `CLAUDE.md`'s first
compounding-friction test.

**Why this item is the head, and no member is.** Confirmed against the store on
2026-09-18. `PL-LKGL` is the measurement `PL-6ZQY` cites and it is `done`
(`#658`): it names the root sentence - the field tests for the presence of the
fix, never for the presence of the fault - decided one facet, and explicitly
refused the recorded fault test, so the general contract was left unwritten.
`PL-0M32` is the sharpest sub-question ("can 'finished under a renamed test' be
told from 'not started' at all") and is scoped to that one ambiguity. `PL-D0K3`
is a policy question about ten specific `doc_check` commands. None settles what
an exit code may be read to mean, and promoting one of them would rank a narrow
item above every band but `P0` where nobody could work the cluster from it.

**Decision needed.** What each consumer may conclude from a `verify:`
command's exit status, and what the field owes beyond a command string:

- whether a **fault test** is recorded beside the fix test, so a command can
  distinguish "the problem is gone" from "the fix landed" (`PL-LKGL` refused
  this once, on a measurement, and the refusal is reopenable on the cluster);
- what a consumer does where the command **cannot run at all** - red
  prerequisite (`PL-T7VS`), timeout (`PL-6YWK`), nothing selected (`PL-Q8RQ`);
- which consumers may **decline to answer** rather than return a verdict;
- what the command owes its own item - that its halves name the tree the item
  touches (`PL-2M4X`, `PL-6YL1`, `PL-LBW5`), not a file that cannot exercise it.

**The items this explains (12, confirmed 2026-09-18 against each brief).**
`PL-T7VS`, `PL-0M32`, `PL-Q8RQ`, `PL-6TN8`, `PL-D0K3`, `PL-3DXV`, `PL-6YWK`,
`PL-2M4X`, `PL-6YL1`, `PL-Y4YX`, `PL-H9GV`, `PL-LBW5`.

Eleven are the 2026-09-17 candidate list, each re-read and still open.
`PL-LBW5` is added: five items' commands `grep` a file their own `touches` does
not declare, which is `PL-2M4X`'s defect generalized, and it carries the
`verify-command-health` feature the project already groups this work under.
Two members carry a second question the head does not settle and are named
here for the half that is the mechanism: `PL-Y4YX` also asks whether
`app/theme.py`'s PySide6 invariant is right, and `PL-H9GV` also owes
`PL-01GD` a test.

**Considered and left out**, each on its own brief rather than on its title:
`PL-8T83` (a 62.6 s command in the scoped replay) and `PL-SHTR` (a nested
replay one level down) are costs of running a command, not readings of its
result; `PL-BGMK` (two items' `touches` and commands overlap and are never
compared) is duplicate detection using `verify:` as evidence; `PL-PFK1` (a
`REJECT` on a self-audited branch) is the commission audit's verdict rather
than the `verify:` command's; `PL-MSFB` and `PL-0HPV` are a stale workaround
and a placement question. Any of them may join on a later reading; none of
them was confirmable from its brief today.

**Done when.** The contract above is decided and written where the consumers
read it - the field's own documentation and `.claude/skills/docket/SKILL.md`'s
`verify:` section - each consumer in `verify.py` and `checks.py` states which
conclusion it is entitled to draw, and the twelve members are re-pointed at the
decision or dropped against it.

**Where this came from.** `PL-6ZQY` found six clusters under one mechanism -
*the apparatus infers a fact it could have recorded* - and `PL-VX5H` built the
way to rank one: `root-cause-of:` on the item that causes the cluster, which
`docket next` then offers above every band but `P0`. Marking the six on
2026-09-17 found only two with a causing item in the store (`PL-BHVM`,
`PL-L4YG`); this item was filed to record that this cluster had none. On
2026-09-18 it became the head itself rather than a tracker of one, which is the
cheaper of the two endings its own `Done when` offered: the diagnosis, the
decision and the membership were already written here, and a separate head
would have been one more item to work.
