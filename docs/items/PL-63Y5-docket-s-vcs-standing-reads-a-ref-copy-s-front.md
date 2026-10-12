---
id: PL-63Y5
title: docket's vcs._standing reads a ref copy's front matter through parse_front_matter in its closure arm, where a block list or block scalar arrives empty, and never asks block_list_keys, so a ref that reopened an item and wrote a field as a block answers behind - nothing stranded - while the removal arm declines the same copy; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
milestone: v0.5.24
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1436
payoff: stranded reports a ref that reopened a closed item with a block-written field, instead of calling it behind and hiding the edit
verify: grep -q 'def test_a_ref_reopening_a_closed_item_with_a_block_field_is_ahead' subprojects/docket/tests/test_vcs.py
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

**Re-confirmed 2026-10-11** on main at `16a20a4f`: `_standing` answers `behind`
for the block-list copy above against the `done` base and for a `reason: |`
copy, and `ahead` for the same block-list copy against a `ready` base.

**Why it matters.** `stranded` is how a session finds work a branch holds and
`main` does not, and `behind` is its word for nothing to recover. A ref that
reopened a closed item and wrote a field as a block is exactly such work, and
this answer hides it.

**Generator check.** A member of `PL-R417`: a surface that drops a shared
reader's named decline and answers from the partial reading, the shape
`PL-GMR6` recorded. It is the gap closed `PL-F7Z6`'s fix left. Latent, so an ordinary item under that head's `spent` verdict: found live in a tracked file, it reopens `PL-R417` (2026-10-11 triage).
`PL-JTP1` (untriaged) groups it with five other callers that drop a shared
reader's decline, and proposes the type-level fix that would close them together.

**Done when.** The closure arm declines a copy `_front_matter_pairs` declines
and answers `ahead`, as the removal arm does; a test pins both forms above.
