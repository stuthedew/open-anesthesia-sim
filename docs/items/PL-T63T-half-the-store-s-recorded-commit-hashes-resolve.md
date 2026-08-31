---
id: PL-T63T
title: "Half the store's recorded commit: hashes resolve nowhere, because the field names the branch commit a squash discards"
status: untriaged
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

**Decision.** Three answers, and they are not equal. Keep recording the branch
commit and accept the decay, since `pr:` is the durable pointer. Record the
landing commit on the default branch instead, which is durable but unknowable
until after the merge - so it would be written by a later pass, not by the
closing commit. Or drop the field and let `pr:` be the only pointer, which is
the smallest store that still answers the question.

**Done when.** One of the three is chosen, the README states what the field
means under a squash-merge policy, and the close-out procedure writes what the
choice says - with a check where the choice makes one decidable.
