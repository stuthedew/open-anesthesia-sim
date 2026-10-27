---
id: PL-0RZN
title: Re-point the two GAP citations in tests/unit/test_record_writes.py from PL-YXGX, dropped as a duplicate in #1845, to PL-DQL9, the open item it was folded into
priority: P2
effort: S
status: done
classes: test
feature: one-source-of-truth
touches: tests/unit/test_record_writes.py
added: 2026-10-27
closed: 2026-10-27
pr: 1845
payoff: the record-writes test passes on #1845, and each blood:gas GAP entry names the open item that holds the fix
verify: ! grep -qF 'PL-YXGX' tests/unit/test_record_writes.py
---

**Problem.** `tests/unit/test_record_writes.py` requires each `GAP` entry to
name an open item. Two entries, for `patient.PatientCompartments.venous_blood`
and `tissue.TissueGroup.blood_gas_partition_coefficient`, named `PL-YXGX`.
`#1845` dropped `PL-YXGX` as a duplicate of `PL-DQL9`.

**Reproduced 2026-10-27.** `checks-part-2` failed on `#1845` with two failures
of `test_a_field_written_without_a_check_at_the_write_says_why`, both
`assert _open_items_named(write.why)` returning `[]`.

**Why it matters.** The test is red on `#1845`, which holds the pull request
back. The two entries also point a reader at a closed item instead of the one
that holds the fix.

**Done when.** Both entries name `PL-DQL9`, and
`tests/unit/test_record_writes.py` passes.
