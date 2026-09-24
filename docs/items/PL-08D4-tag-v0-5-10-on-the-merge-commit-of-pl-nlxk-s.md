---
id: PL-08D4
title: Tag v0.5.10 on the merge commit of PL-NLXK's cut: the release is cut and only the project owner can push a tag ref from this environment
priority: P2
effort: S
status: ready
classes: planning
feature: release-process
touches: docs/items/
added: 2026-09-24
payoff: v0.5.10 carries its annotated tag, so the next cut is not refused and git describe resolves across it
not-delegable: Proving this means pushing a tag ref to the remote, which no session in this environment can do: PL-N936 measured the failure, a dry run reporting [new tag] and the real push dying on an unexpected disconnect
---

**Problem.** Tag v0.5.10 on the merge commit of PL-NLXK's cut: the release is cut and only the project owner can push a tag ref from this environment

**`PL-NLXK` cut v0.5.10 and stopped where the tooling stops.** `bin/docket
release` deliberately does not tag: the bump and the notes are reviewed first,
and the tag then goes on the merge commit rather than on any branch commit.

**Which commit.** The cut arrives in `#989`, opened as a draft at the branch's
first push so that it could not be merged before the cut was pushed
(`PL-H14W`). Its squash merge's subject ends `(#989)`, which the second
command below resolves. If it resolves nothing, `git tag` fails on an empty
ref rather than tagging the wrong commit.

```bash
git fetch origin main
git tag -a v0.5.10 "$(git log origin/main -1 --format=%H --grep='cut v0.5.10.*(#989)$')" -m "v0.5.10"
git push origin v0.5.10
```

**Why it matters.** `bin/docket release` refuses to cut the next release while
the previous one is untagged, because a release cut without a tag leaves a
permanent gap that `git describe --contains` resolves nothing across. Nothing
in the tree reports it either, so `git ls-remote --tags origin v0.5.10` is the
only answer.

**Done when.** `git ls-remote --tags origin v0.5.10` resolves, on the merge
commit of `#989`.

**Generator check.** Bookkeeping: the owner's step after every cut, because
`PL-N936` measured that no session in this environment can push a tag ref.
`docket new` recorded this filing as a recurrence of `PL-LRP2`, the same step
for v0.5.9, which is that design recurring rather than a defect firing again.
