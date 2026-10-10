---
id: PL-4DM0
title: docket verify's queue-edit audit compares the block lists and block scalars docket.model declines only for equality, so an edit inside a declined block - a block scalar's lines, a touches block list gaining an entry - beside an added pr or recurrences entry passes as the sanctioned write; latent
status: untriaged
feature: one-answer
added: 2026-10-10
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

**Generator check.** A member of `PL-R417`: a surface that drops a shared
reader's named decline and answers from the partial reading, the shape
`PL-GMR6` recorded. It is the gap closed `PL-24MT`'s fix left.

**Done when.** The audit refuses to call an edit sanctioned where either copy
holds a declined block list, block scalar or unread line, and a test pins both
forms above.
