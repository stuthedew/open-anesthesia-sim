---
id: PL-WM46
title: verify's batch NOTE reads any id a commit subject mentions as a batch claim, and prints every audited commit as naming it, so a closure whose one subject cited PL-9RFP mid-sentence read as 4 commits also naming PL-9RFP
status: untriaged
added: 2026-09-23
---

**Problem.** verify's batch NOTE reads any id a commit subject mentions as a batch claim, and prints every audited commit as naming it, so a closure whose one subject cited PL-9RFP mid-sentence read as 4 commits also naming PL-9RFP

**Found closing `PL-19T3`, 2026-09-23.** `bin/docket verify --self PL-19T3`
printed `NOTE the audited diff is this item's alone - 4 commit(s) also name
PL-9RFP, so the paths above are the batch's rather than this item's`. One of
the four subjects mentions `PL-9RFP`, mid-sentence ("run PL-9RFP's
changed-paths replay test with git"), and none leads with it. So the branch
was no batch, and the paths were this item's alone.

Two causes, both in `verify.py`:

- `other_items_named` matches `ID_PATTERN` anywhere in `git show -s
  --format=%s`, but `CLAUDE.md` has an item claimed only by an id that *leads*
  a subject. `vcs.leading_ids` already reads it that way. A subject citing
  another item is a citation, not a batch.
- The message prints `len(commits)`, every audited commit, not the number
  that name the other id.

Advisory in both audit modes, so it never refuses. But it states something
false about the diff, and a NOTE that fires on a plain citation is one that
readers learn to skip. The likely route is to read each subject's leading ids
and count the commits that carry one. That is `PL-4LT9`'s own case, a commit
closing several items leading with all of them, and it stays covered.
