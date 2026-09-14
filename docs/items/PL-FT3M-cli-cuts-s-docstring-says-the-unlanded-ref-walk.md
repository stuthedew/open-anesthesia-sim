---
id: PL-FT3M
title: cli._cuts's docstring says the unlanded-ref walk is gated on the release offer, where it is gated on Readiness.is_worth_cutting - and the two now diverge routinely
priority: P3
effort: S
status: ready
classes: docs, defect
feature: release-process
touches: subprojects/docket/src/docket/cli.py
added: 2026-09-14
verify: uv run pytest tests/unit/test_docket_digest_hook.py && ! grep -q 'Gated on the offer rather than run for every digest' subprojects/docket/src/docket/cli.py
---


**Problem.** cli._cuts's docstring says the unlanded-ref walk is gated on the release offer, where it is gated on Readiness.is_worth_cutting - and the two now diverge routinely

**Verified 2026-09-14.** `subprojects/docket/src/docket/cli.py:455` gates the
call on `ready.is_worth_cutting`, while `_cuts`'s own docstring at `:462-470`
says it is "read only where a release is being offered" and "Gated on the offer
rather than run for every digest". Those are different predicates, and this
session's own digest shows them apart: it printed `Releasable: 10 finished
item(s) since 0.4.24` - so `is_worth_cutting` is true - beside `No release to
offer`, because the version a bump would reach is reserved.

**Why it matters.** The docstring is the record of why the walk is gated at all,
and it now describes a narrower gate than the code uses, so a reader deciding
whether the 103 ms walk is justified is reasoning from a predicate that is not
the one in force. That the two diverge *routinely* rather than at an edge is
what makes it worth fixing: the reserved-version case is now the normal case
between milestones.

**Done when.** `_cuts`'s docstring names `Readiness.is_worth_cutting` as the
gate and says what that means - there is finished work to cut, whether or not a
version is free to cut it at - rather than describing it as the release offer.
