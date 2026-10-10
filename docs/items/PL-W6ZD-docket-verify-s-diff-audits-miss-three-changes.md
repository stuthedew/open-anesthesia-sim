---
id: PL-W6ZD
title: docket verify's diff audits miss three changes - a skip decorator moved from one test to another cancels in the per-file fold, a merge commit's combined diff is read as a two-way one, and an uncommitted edit beside a sanctioned queue write is never read - so a suppression, an added line or a status edit passes unseen; latent
status: untriaged
added: 2026-10-10
---

**Problem.** docket verify's diff audits miss three changes - a skip decorator moved from one test to another cancels in the per-file fold, a merge commit's combined diff is read as a two-way one, and an uncommitted edit beside a sanctioned queue write is never read - so a suppression, an added line or a status edit passes unseen; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`docket.verify`.

- `added_suppressions` cancels an added logical line against a removed one
  anywhere in the same file, so `@pytest.mark.skip(reason="needs bash")` moved
  from `test_a` to `test_b`, with nothing else changed, reports no suppression
  added, though it now disables a different test.
- `_net_line_changes` reads `git show --format=` output for a merge commit led
  by the item's id, which git writes as a combined diff headed `diff --cc`
  with two-column prefixes (`++`, ` +`, `- `). It skips a `++` line as a
  `+++` header and never resets the path on `diff --cc`, so
  `++xfail_strict = false` in a `pytest.ini` is dropped and the check passes.
  `PL-MR8Z` holds the two-way header misreads; this is the combined format.
- `sanctioned_queue_edit` and `_changes` read commits only, so an uncommitted
  `status: done` or `verify: true` edit on an item file whose committed change
  is a `pr` write still answers `pr`, while `changed_paths` lists the path.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, on scratch repositories. Latent: no commit on `main` moves a
decorator this way, merges carry no item's id, and the working-tree case needs
an uncommitted edit at verify time.

**Generator check.** Not a member of `PL-R417`: each statement is read whole;
what is misread is its position, the diff's format, or which tree is read.

**Done when.** A suppression is compared with the definition it decorates, a
combined diff is read as one or declined by name, and an uncommitted change to
a path the audit judges is refused or named; a test pins each.
