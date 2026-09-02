---
id: PL-T63T
title: "Half the store's recorded commit: hashes resolve nowhere, because the field names the branch commit a squash discards"
priority: P2
effort: S
status: done
closed: 2026-09-02
pr: 236
classes: defect, infra
feature: commit-provenance
touches: subprojects/docket/README.md, .claude/skills/docket/SKILL.md, subprojects/docket/src/docket/checks.py
added: 2026-08-31
---
**Problem.** A closed item records `commit:` as the hash on the branch that
did the work. `PL-S4M2` made `main` squash-merge, so that commit never reaches
the default branch and becomes unreachable the moment the head branch is
deleted. Measured in this checkout on 2026-08-31, over the 83 items carrying
the field: 21 hashes are reachable from `origin/main`, 21 are present in the
object store but reachable from nothing, and 41 sit below this shallow clone's
horizon and cannot be judged. So roughly half of what can be checked is a
pointer to nowhere, and the proportion grows with every squash-merged item.

`subprojects/docket/README.md` already predicts this - "it stops being
resolvable the moment a project squash-merges ... which is how a hash that
resolves nowhere gets in" - and answers it with `pr:`, which survives. The
finding is not that the decay is unknown. It is that the field is still being
written with the value that decays when the durable one is equally knowable:
the squash commit on the default branch, which GitHub writes with the pull
request number in its subject and which `merged_pull_requests` already parses.

**Why it matters.** Provenance is the whole point of a closed item: it is how
a reader gets from a line of behaviour to the reasoning that chose it. `pr:`
carries that, so nothing is lost today - but a reader handed two pointers, one
of which resolves and one of which does not, has to learn which to trust, and
a `git show` on the recorded hash fails with nothing said about why.

**Where.** The `commit:` field's meaning, in `subprojects/docket/README.md`'s
"Provenance survives the merge strategy"; whatever writes it at close-out
(`.claude/skills/docket/SKILL.md`, "Mode: close out an item"); and possibly a
`docket check` rule, since reachability is decidable in a complete clone and
must decline in a shallow one the way `merged_pull_requests` does.

**Decision needed.** Three answers, and they are not equal. Keep recording the branch
commit and accept the decay, since `pr:` is the durable pointer. Record the
landing commit on the default branch instead, which is durable but unknowable
until after the merge - so it would be written by a later pass, not by the
closing commit. Or drop the field and let `pr:` be the only pointer, which is
the smallest store that still answers the question.

**Done when.** One of the three is chosen, the README states what the field
means under a squash-merge policy, and the close-out procedure writes what the
choice says - with a check where the choice makes one decidable.

**Triaged 2026-09-01.** P2, `defect`/`infra`, `commit-provenance`. Left out of
v0.2.8's frozen list on the precedent already recorded there for `PL-68XK`
(hold a recorded `commit` hash to one that resolves): the `commit:` field
predates the freeze and was excluded from the approved list deliberately. This
item is the same field one step earlier - what should be written, rather than
what should be checked - so the two are one decision and should be answered
together, `PL-T63T` first.

**Decided 2026-09-02 (project owner).** Drop the field. `pr:` is the only
provenance pointer; `commit:` is retired and must not be written into a new
closure. The two rejected answers, and why:

- *Record the landing commit on the default branch.* Durable, but unknowable
  until after the merge, so it cannot be written by the closing commit. It
  would need a second pass over every closed item, forever, to produce a
  second pointer to the change `pr:` already reaches.
- *Keep the branch commit and accept the decay.* Cheapest, and it knowingly
  keeps a field that resolves nowhere about half the time while reading as
  provenance - which is the first of the three tests `CLAUDE.md` now uses to
  decide what interrupts feature work: it gives a wrong answer silently.

**What landed.** `subprojects/docket/README.md`'s "Provenance survives the
merge strategy" states the retirement and carries the 2026-08-31 measurement;
`.claude/skills/docket/SKILL.md`'s close-out step says not to write the field.
The 66 recorded values are left in place as a historical record rather than
stripped, per the same decision.

**No check enforces this, deliberately.** Erroring on a newly written `commit:`
needs a cutover date, since every existing value has to stay legal - a second
`verify_required_from`-shaped knob, and a permanent one, to guard a field that
`docket new` does not write and the close-out step now tells a session in bold
not to write. That fails `CLAUDE.md`'s test for building a mechanism: the risk
does not recur often enough to pay for the machinery. `PL-68XK` was dropped for
the matching reason - it existed to validate this field.

