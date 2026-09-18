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
root-cause-of: PL-99YZ, PL-HX5C, PL-KSCW, PL-LF2C, PL-MBTZ, PL-Q9Z1, PL-R808, PL-SH9Q, PL-SY1J, PL-WNQT
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

**The `r_vcs = 1.05` figure above does not survive measurement, 2026-09-17
(`PL-M2SD`).** That number counted *every* item spawned by work on a `vcs.py`
item, including captures about unrelated parts of the tree. Counting only
children that land back in `vcs.py` — which is what "this cluster generates its
own work" claims — gives **r_vcs = 0.71**, below 1.0. The cluster closes more
than it creates. Two attribution bugs fixed in `tools/generator_check.py`
account for the rest of the gap: a multi-title `bin/docket new` commit made
each captured item the others' parent, and a `touches` entry written
`docs/items/` escaped the store exclusion.

On the corrected measure **no cluster in this repository reports at all**, and
`vcs.py` is not the lane's worst: `docs/MODEL.md` carries 40 open items at
0.55, `ROADMAP.md` 32. `vcs.py` has 12 open of 67, and its filings fell 26 to
14 over the two weeks to 09-17.

**What this retracts, and what it does not.** The urgency framing is retracted:
this is not a runaway generator and should not be ranked as one. The design
argument is untouched and is the reason to keep this item — nineteen items each
choosing their own answer to one question is duplication, and it is counted
from the items themselves rather than from any spawn rate. So the case for one
design round still holds; the case for doing it *ahead of everything else* does
not.

**Ranked as a generator after all - on the other definition (2026-09-17,
`PL-VX5H`).** What the paragraph above retracts is a *ratio*, and the ratio was
never the definition. `CLAUDE.md` now makes a mechanism causing three or more
items a generator and ranks it above everything but `P0`, and the count this
item argues from - items each choosing their own answer to one question - is
that definition exactly. Both readings stand: on the spawn rate this is not
runaway, and on the recorded definition it is a generator, so the
`root-cause-of:` line in the front matter is the claim and `docket next` now
offers this ahead of every band but `P0`.

The ten ids it names are the open items still re-deciding what evidence proves
a claim on a ref is done - the `stranded`/`flight`/`show` content comparisons
(`PL-SH9Q`, `PL-WNQT`, `PL-MBTZ`, `PL-KSCW`, `PL-SY1J`, `PL-Q9Z1`), the exact
ref test and the premise it rests on (`PL-R808`, `PL-LF2C`), and the two
records of guards passing while two sessions duplicated work anyway
(`PL-HX5C`, `PL-99YZ`). Ten rather than the title's nineteen because nine
closed as one round on 2026-09-13, which `PL-CSHL` records and measures.

Deliberately not named: items that merely declare `vcs.py`. `PL-GVC0` (the
hard-coded `PL-` id prefix), `PL-3LLZ` (four test fakes teaching the same git
question) and `PL-7XNX` (one `git diff` per ref rather than per file, which its
own brief calls "not a correctness question") are in the same file and are not
this decision.
