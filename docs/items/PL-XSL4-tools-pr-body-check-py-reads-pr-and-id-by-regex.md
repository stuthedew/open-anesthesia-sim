---
id: PL-XSL4
title: tools/pr_body_check.py reads pr: and id: by regex over an item's first 2000 characters and takes ids from anywhere in a subject rather than vcs.leading_ids, so a long front matter or a mid-subject citation answers differently from the store's reader
status: untriaged
feature: recorded-not-inferred
added: 2026-10-01
---

**Problem.** tools/pr_body_check.py reads pr: and id: by regex over an item's first 2000 characters and takes ids from anywhere in a subject rather than vcs.leading_ids, so a long front matter or a mid-subject citation answers differently from the store's reader

**Recorded alternative, from the 2026-10-01 survey.** Use the store reader for `pr:` and `id:` and `vcs.leading_ids` for a subject. It writes recovery records rather than refusing, so a wrong read is written into the store. Shape B.
