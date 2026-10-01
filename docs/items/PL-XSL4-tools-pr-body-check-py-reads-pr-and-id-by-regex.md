---
id: PL-XSL4
title: tools/pr_body_check.py reads pr: and id: by regex over an item's first 2000 characters and takes ids from anywhere in a subject rather than vcs.leading_ids, so a long front matter or a mid-subject citation answers differently from the store's reader
priority: P2
effort: S
status: done
classes: defect
feature: recorded-not-inferred
touches: tools/pr_body_check.py, tests/unit/test_pr_body_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
closed: 2026-10-01
pr: 1271
payoff: the recovery record pr_body_check writes into the store reads pr:, id: and a subject's ids the way the store does, so a long front matter or a cited id cannot write a wrong record
verify: ! grep -qF '[:2000]' tools/pr_body_check.py && ! grep -qF 're.findall(ID_PATTERN, subject)' tools/pr_body_check.py
---

**Problem.** tools/pr_body_check.py reads pr: and id: by regex over an item's first 2000 characters and takes ids from anywhere in a subject rather than vcs.leading_ids, so a long front matter or a mid-subject citation answers differently from the store's reader

**Recorded alternative, from the 2026-10-01 survey.** Use the store reader for `pr:` and `id:` and `vcs.leading_ids` for a subject. It writes recovery records rather than refusing, so a wrong read is written into the store. Shape B.

**Why it matters.** `pr_body_check.py` writes recovery records into the store rather than refusing, so a `pr:` or `id:` it misreads is written down as fact. Its reader stops at 2,000 characters where the store's reads the whole front matter, and its subject reader takes every id in a subject where `vcs.leading_ids` takes the leading ones, so a long front matter or a subject citing a second id answers differently from docket.

**Reproduced 2026-10-01.** Five item files carry a front matter over 2,000 characters today, none with `pr:` past that point, so the 2,000-character read is right on every file and wrong on the sixth by construction. `tools/pr_body_check.py:496-498` is that read and `:513` (`re.findall(ID_PATTERN, subject)`) the subject read.

**Done when.** `pr:` and `id:` are read through the store reader, subjects through `vcs.leading_ids`, and a test pins each: a `pr:` past 2,000 characters found, a mid-subject id not taken as leading.

**Generator check.** An instance of `PL-PVW2`'s fact - which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it - filed after that head drained on 2026-09-26. Six such instances filed 2026-10-01 make `PL-KGYT`, this item's head.
