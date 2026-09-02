---
id: PL-B0YN
title: docket next ranks by smallest effort among items in underway features, not by which feature is nearest completion, so its rationale line and CLAUDE.md both describe a ranking the code does not implement
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/tests/test_plan.py
added: 2026-09-02
closed: 2026-09-02
pr: 186
verify: uv run pytest subprojects/docket/tests/test_plan.py && grep -q 'def test_the_feature_nearest_completion_outranks_a_smaller_item' subprojects/docket/tests/test_plan.py
---

**Problem.** `plan.py`'s `rank()` returns
`(hotfix, placement, band, finishes, sort_key()[1], identifier)`, where
`finishes` is **binary** — 0 if the item belongs to any underway feature, 1 if
not — and `sort_key()[1]` is the effort index. There is no term anywhere in the
tuple for how near a feature is to completion. Among two items in the same
band, both in underway features, the winner is therefore simply the smaller
effort, then the lower id.

Observed 2026-09-02 immediately after cutting v0.2.9, when three landed items
joined `presentation-safety`:

```
1. P1 PL-NV9W ... (S)  Finishes 'presentation-safety', which is 30% done (7 item(s) left).
                       A shipped feature beats progress on several.
2. P1 PL-0MLQ ... (M)  Finishes 'numerical-domain', which is 75% done (2 item(s) left).
                       A shipped feature beats progress on several.
```

The item in the feature that is 30% done with seven left is ranked above the
one in the feature that is 75% done with two left, and the rationale line given
for the first is the argument for the second.

**Why it matters.** Three artifacts state the stronger rule, and none of them
is true of the code:

1. The rationale line itself — "A shipped feature beats progress on several" —
   is printed beside a ranking that did not apply it.
2. `CLAUDE.md`'s "Prefer finishing a feature to advancing several" says
   `bin/docket next` "already ranks this way within a priority band; do not
   override it toward novelty". A session that follows that instruction defers
   to a ranking that is really effort-ascending.
3. `PL-G1MF`, which covers the *wording* of the same line, asserts in its own
   brief that "the ranking it explains is sound: the tie-break really is
   'prefer the feature nearer completion'". It is not, so fixing `PL-G1MF` as
   written would put a more careful sentence on top of the same wrong order.

This is the command every session leads with, so the cost is paid once per
session and lands on the choice of what to work on.

**Where.** `subprojects/docket/src/docket/plan.py`, `rank()` and the
`elif item.identifier in underway:` rationale branch;
`subprojects/docket/tests/test_plan.py` beside it. `CLAUDE.md`'s "Prefer
finishing a feature" bullet is read against whatever is decided, and edited if
the decision is that effort-ascending is the intended order.

**Worth deciding first.** Which order is actually wanted. Two candidates:

- **Rank by remaining open items in the feature**, ascending, so the feature
  nearest completion wins — the rule all three artifacts already claim. Makes
  the printed rationale true as written.
- **Keep effort-ascending and correct the prose instead**, on the argument that
  a small item shipped today beats a larger one that finishes a feature
  tomorrow. Defensible, but then `CLAUDE.md` and the rationale line both say
  the wrong thing today and must change.

The first is preferred: three documents already specify it, and it is the rule
the project owner has been acting on.

**Relation to PL-G1MF.** `PL-G1MF` fixes the sentence; this fixes what the
sentence describes. Whichever is done second should re-read the other's brief,
and `PL-G1MF`'s claim about the tie-break needs correcting either way — they
are close enough that working them together is likely cheaper than twice.

**Found.** 2026-09-02, while confirming `docket next`'s recommendation after
cutting v0.2.9.

**Done when.** `bin/docket next`'s order within a band matches the rule its
rationale line states, `CLAUDE.md` and `PL-G1MF` agree with the implemented
order, and a test pins the case above: two ready items of equal band in
underway features of different completeness, where the smaller-effort item is
in the less complete feature.
