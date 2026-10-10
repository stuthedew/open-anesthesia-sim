---
id: PL-63Y5
title: docket's vcs._standing reads a ref copy's front matter through parse_front_matter in its closure arm, where a block list or block scalar arrives empty, and never asks block_list_keys, so a ref that reopened an item and wrote a field as a block answers behind - nothing stranded - while the removal arm declines the same copy; latent
status: untriaged
feature: one-answer
added: 2026-10-10
---

**Problem.** docket's vcs._standing reads a ref copy's front matter through parse_front_matter in its closure arm, where a block list or block scalar arrives empty, and never asks block_list_keys, so a ref that reopened an item and wrote a field as a block answers behind - nothing stranded - while the removal arm declines the same copy; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`docket.vcs`. `_standing`'s closure arm compares a
ref's copy with the base's through `docket.model.parse_front_matter`, whose
docstring says a block list arrives empty and is reported by
`block_list_keys`; `_standing` never asks. Its body test never sees the front
matter. The removal arm reads the same copy through `_front_matter_pairs` and
declines it, so one continued value answers `ahead` in one arm and `behind` in
the other.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against PyYAML 6.0.3 and ruamel.yaml 0.19.1, which read the ref's
`touches` as two paths:

```text
base (closed the item):     ref:
status: done                status: ready
touches: a                  touches:
                              - a
                              - src/new_module.py
```

`_standing` answers `behind` and `stranded` reports no edit; a `reason: |`
block scalar gives the same, while the same copies with equal status answer
`ahead`. Latent: no item file carries a block list, block scalar or unread
line, but a ref's copy is exactly a copy that has not passed `docket check`.

**Generator check.** A member of `PL-R417`: a surface that drops a shared
reader's named decline and answers from the partial reading, the shape
`PL-GMR6` recorded. It is the gap closed `PL-F7Z6`'s fix left.

**Done when.** The closure arm declines a copy `_front_matter_pairs` declines
and answers `ahead`, as the removal arm does; a test pins both forms above.
