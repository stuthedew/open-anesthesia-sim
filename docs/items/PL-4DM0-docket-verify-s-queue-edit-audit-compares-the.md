---
id: PL-4DM0
title: docket verify's queue-edit audit compares the block lists and block scalars docket.model declines only for equality, so an edit inside a declined block - a block scalar's lines, a touches block list gaining an entry - beside an added pr or recurrences entry passes as the sanctioned write; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, subprojects/docket/README.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1431
payoff: a touches widened or a value rewritten inside a block the item reader declines can no longer ride a pr or recurrence write past the queue-edit audit as sanctioned
verify: grep -q 'def test_an_edit_inside_a_declined_block_is_not_a_sanctioned_queue_edit' subprojects/docket/tests/test_verify.py
---

**Problem.** docket verify's queue-edit audit compares the block lists and block scalars docket.model declines only for equality, so an edit inside a declined block - a block scalar's lines, a touches block list gaining an entry - beside an added pr or recurrences entry passes as the sanctioned write; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`docket.verify`. `_pr_recorded` and
`_recurrences_grew`, rewritten in `#1389` (`PL-24MT`), read both copies through
`docket.model._front_matter_pairs`, which declines a YAML block list or block
scalar (YAML 1.2.2 § 8.2.1, § 8.1) by naming its key and giving it an empty
value, so nothing downstream reads half a value as the whole. The audit
compares those names and empty values for equality, so a change to the
declined lines is invisible to it.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against PyYAML 6.0.3, which reads each content change:

```text
reason: >-
  old words          ->  new words, with pr: 5 added
touches:
  - a                ->  - src/core.py added, with pr: 5 added
```

`sanctioned_queue_edit` answers `pr` for both. Latent: no item carries a block
list, block scalar or unread line, and `docket check` errors on each by name.

**Re-confirmed 2026-10-11** on main at `16a20a4f`: `_queue_kind` answers `pr`
for both forms above, the folded `reason:` rewritten and a `touches` block list
gaining `src/core.py`, each beside an added `pr: 5`.

**Generator check.** A member of `PL-R417`: a surface that drops a shared
reader's named decline and answers from the partial reading, the shape
`PL-GMR6` recorded. It is the gap closed `PL-24MT`'s fix left.

**Why it matters.** The `pr` and `recurrence` exemptions are safe only
because each is mechanically distinguishable from tampering, and `verify`
passes an out-of-`touches` item edit on their word. Read by name alone, a
declined block lets a widened `touches` or a rewritten `reason:` ride a
`record` write as the sanctioned kind. Latent: `docket check` refuses every
block form by name, so such a branch fails `make check` beside the audit
today, but the audit's own line still answers wrongly.

**Done when.** The audit refuses to call an edit sanctioned where either copy
holds a declined block list, block scalar or unread line, and a test pins both
forms above.

**Done 2026-10-12** (`#1431`). `verify._declines` says whether
`_front_matter_pairs` declined any of a copy - a block list, a block scalar, or
a line continuing nothing - and `_pr_recorded` and `_recurrences_grew` refuse a
copy on either side that holds one, so an edit inside a declined block can no
longer ride a `pr` or recurrence write as the sanctioned kind. `capture` is
unchanged: a created file has no prior content for an edit to hide in. Pinned by
`test_an_edit_inside_a_declined_block_is_not_a_sanctioned_queue_edit` in
`subprojects/docket/tests/test_verify.py`, four cases (both forms above, the
block list beside a recurrence, and a `pr` write onto a copy holding an unread
line), each red on main's `verify.py`. `subprojects/docket/README.md` says the
exemption does not reach such a copy.
