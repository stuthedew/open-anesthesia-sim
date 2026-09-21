---
id: PL-7H9Y
title: PL-KFWL's stated symptom does not reproduce on 2026-09-21: v0.4.8 resolves to the #440 release-cut commit and doc_check reports 0 errors, so the item is either stale or names a condition nothing records
priority: P3
effort: S
status: dropped
classes: housekeeping
added: 2026-09-21
closed: 2026-09-21
reason: PL-KFWL already carries the correction this item asked for: its brief records (2026-09-19, under PL-6ZQY) that v0.4.8 was cut rather than withdrawn, and narrows its own Done when to the tag-ahead-of-cut guard alone. The residue it correctly names - a title that still describes the resolved half, and a verify: opening on a doc_check run that passes today - is repaired by the session that starts PL-KFWL, under repair-as-started.
not-delegable: Dropped on a re-read of PL-KFWL rather than on a command. There is nothing to run: the work this item asked for was recorded in that item two days before this one was filed.
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

**Dropped on triage, 2026-09-21, because the premise was already answered in
the item it is about.** `PL-KFWL`'s own brief carries the correction, made
2026-09-19 under `PL-6ZQY`'s crossing-lane sweep: v0.4.8 was resolved by the
first of the two dispositions offered above - it was *cut*, not withdrawn - the
tag sits on the cut commit, the version table carries its row, and `doc_check`
is green. That brief then narrows its own `Done when` to the second clause
only, the guard against a tag pushed ahead of its cut, and says in so many words
that what is left of the item is that guard and nothing else. So both dispositions
this item asked for had already been taken, and the measurement recorded above -
correct as far as it goes - confirms a correction rather than finding a stale
item.

**What it was right about, and where that goes.** Two things it names are still
true of `PL-KFWL` and are neither dropped nor re-filed here. Its title still
describes the tag fault rather than the guard, which is what `bin/docket next`
shows a reader; and its `verify:` still opens on a `doc_check` run that passes
today, which is the prerequisite-clause shape the store repairs as each item is
started rather than in a pass. Both are repairs that belong to the session that
starts `PL-KFWL`, under the repair-as-started rule, which is why this is a drop
and not a re-pointing.
