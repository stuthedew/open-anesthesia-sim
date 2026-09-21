---
id: PL-7H9Y
title: PL-KFWL's stated symptom does not reproduce on 2026-09-21: v0.4.8 resolves to the #440 release-cut commit and doc_check reports 0 errors, so the item is either stale or names a condition nothing records
status: untriaged
added: 2026-09-21
---

**Problem.** PL-KFWL's stated symptom does not reproduce on 2026-09-21: v0.4.8 resolves to the #440 release-cut commit and doc_check reports 0 errors, so the item is either stale or names a condition nothing records

**Measured 2026-09-21** in a fresh container checkout of `main`:

```
$ git log -1 --format='%h %s' v0.4.8
b340e7ff PL-BKDP: cut v0.4.8 - the gate that was measuring itself, and the run that became its own score (#440)
$ python3 tools/doc_check.py check
documentation: 0 errors, 0 advisories
```

So the tag sits on the cut commit and the error `PL-KFWL` describes does not
fire. `PL-KFWL` is `ready`, `P2`, filed 2026-09-07, and its own `verify:`
begins `python3 tools/doc_check.py check`, which passes today - meaning half
its verify command is already satisfied by a tree nobody fixed.

**Why it matters.** An open item whose symptom cannot be reproduced is offered
by `bin/docket next` like any other, and the session that takes it spends its
first half hour discovering there is nothing to fix. `PL-LT77` (same feature,
`tag-error-names-its-cause`) is the reason this is not simply a stale item to
drop: `doc_check` reads **local** tags and `git fetch --tags` does not prune,
so a checkout that fetched a since-withdrawn tag still fails while a fresh one
passes. This container is a fresh one. So the honest disposition is one of
two, and the evidence for choosing is not in this checkout:

- the withdrawn tag was re-pushed onto the cut commit and `PL-KFWL` is done in
  fact - close it, and let `PL-LT77` keep the durable half; or
- it still reproduces in a warm checkout, in which case the item's **Problem.**
  is wrong about its own trigger and should say "in a checkout holding the
  withdrawn tag" rather than "for every session".

**Done when.** `PL-KFWL` is either closed with the tag evidence recorded, or
its brief names the checkout condition that makes it fire.
