---
id: PL-B8HZ
title: verify --self decides one contract field at a time whether to read the base's or the branch's copy of the item, so each field's wrong choice arrives as its own item - six so far, PL-PZ6T and PL-TKFD open
priority: P2
effort: M
status: needs-decision
classes: defect
feature: verify-close-out
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-23
payoff: One stated rule for which copy each contract field is read from, so a new field stops costing an item per wrong direction
root-cause-of: PL-KSV2, PL-PZ6T, PL-TKFD, PL-ZMGR, PL-K4R5, PL-YZJD
generator: live - verify --self chooses the base's or the branch's copy one contract field at a time, and PL-PZ6T (verify:) and PL-TKFD (falsifies:) are still open; every further contract field needs its own choice
---

**Problem.** verify --self decides one contract field at a time whether to read the base's or the branch's copy of the item, so each field's wrong choice arrives as its own item - six so far, PL-PZ6T and PL-TKFD open

**Found 2026-09-23** by `PL-T7Y1`'s generator audit. `PL-5MYR` listed this as
"a bounded tail and not a generator". Three critics each found it a generator
by count (3 of 3). Under `CLAUDE.md`'s rule the count decides the record, and
a bounded tail is an argument about the verdict, not about the record.

**The mechanism.** `verify --self` reads each field of an item's contract from
one of two copies, the base's or the branch's, and the choice is made field by
field as each wrong choice is found. Branch-side reads give false ACCEPTs, and
base-side reads give false REJECTs:

- `PL-KSV2` (done): `not-delegable:` was read from the branch, so a close-out
  could delete its failing `verify:` and ACCEPT. Fixed by `Commission.verify`.
- `PL-PZ6T` (open): `verify --self` runs the branch's `verify:` command
  (`verify.py:2378`), so a weaker passing command can replace a failing one.
- `PL-ZMGR`, `PL-K4R5` and `PL-YZJD` (done): `falsifies:` is read from the
  base's copy, so the session that knows the string cannot declare it.
  `PL-YZJD` is also listed under `PL-4W2L`, which the critics call a
  misattribution: `PL-4W2L` retired the assertion line matcher and never
  touched this read.
- `PL-TKFD` (open, needs-decision): the base-side residual of `falsifies:`.
  A `ready` item's mid-work discovery, and an item captured and closed on one
  branch, still have no route.

**Why it matters.** Every new contract field will need its own copy decision,
and each wrong one costs an item. `PL-5MYR`'s "the fields are four, three are
decided" leaves out `PL-TKFD`, which is the open end of a field it calls
decided.

**Decision needed.** Should every contract field `verify --self` reads come from one copy, the base's with a named exception for fields whose deciding is the work, or should the per-field choice stay and this head close spent? Recommendation: one rule, stated in `verify.py` beside `Commission`, because `PL-PZ6T` and `PL-TKFD` are the same question asked from opposite directions.

**Done when.** One rule says which copy each contract field is read from, and
why. Either it is stated once where every field reader applies it, or the
owner decides the per-field choice stays and this head is closed spent with
that recorded. The pause in `CLAUDE.md` § "What this project is" applies to
any new check this needs.
