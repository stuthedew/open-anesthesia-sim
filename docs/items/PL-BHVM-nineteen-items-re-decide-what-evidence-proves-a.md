---
id: PL-BHVM
title: Nineteen items re-decide what evidence proves a ref is done, seventeen of them in vcs.py: one design round rather than nineteen heuristic patches
priority: P2
effort: M
status: needs-decision
classes: defect, refactor
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-12
---

**Problem.** Nineteen items re-decide what evidence proves a ref is done, seventeen of them in vcs.py: one design round rather than nineteen heuristic patches

**Why it matters.** This is the largest single cluster in the workflow lane and
the only one whose self-generation rate has been measured against a real
baseline: items declaring `subprojects/docket/src/docket/vcs.py` number 53, 38
are closed, and those 38 spawned 40 further items - `r_vcs = 1.05` against a
whole-lane 0.69 (`PL-CSHL`, which fixes the prediction in advance). The cluster
generates more work than it closes, and more than any other part of the lane.

The mechanism is the one `PL-6ZQY`'s map named under 47% of the workflow lane:
**the apparatus infers a fact it could have recorded.** Nothing is written down
when a session claims work, so `stranded`, `flight`, `orphaned` and the digest
each reconstruct the claim afterwards by comparing file content against the
base - and content is unchanged by a squash, by a history rewrite, and by two
sessions writing identical `docket record` lines, which is exactly the set of
cases where the answer is wrong. Each inference fails in a new way, each failure
is found singly, and each becomes its own item. Patching one closes an item and
leaves the generator running; deciding once what evidence proves a ref is done
closes the cluster.

`PL-VV4D` is what a decided instance looks like: it settled that the exact test
is a ref comparison against `refs/pull/<n>/head`, and `PL-R808` is the build.
`PL-LF2C` then found that even that premise is not permanent. Nineteen open
items are still each choosing their own answer.

**Decision needed.** What evidence the apparatus treats as proof that a ref is
done - recorded at the moment a session claims or lands work, or inferred
afterwards from content and refs - and whether the nineteen open items are then
closed as one round against that decision or left to be patched individually.
The sub-questions the decision has to settle: whether a claim is recorded in the
store, in the commit trailer, or not at all; what the answer is where the
evidence is unreachable (no network, no permission, no such ref - `PL-LF2C`'s
three decline conditions generalise); and whether `vcs.orphaned`'s content
comparison stays as the portable fallback or is retired once an exact test
exists.

**Done when.** The decision is recorded with its reasoning and its costs, the
nineteen items are re-pointed at it or dropped against it, and `PL-CSHL`'s count
of what the round spawns can be taken.
