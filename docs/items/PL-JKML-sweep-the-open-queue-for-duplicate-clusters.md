---
id: PL-JKML
title: Sweep the open queue for duplicate clusters filed before bin/docket new could warn on a near-duplicate
priority: P2
effort: M
status: ready
classes: housekeeping
touches: docs/items
added: 2026-09-20
payoff: stops the queue offering one defect as two or three separate items, so a session no longer picks up work another session has already diagnosed and written a verify command for
verify: grep -q '^status: dropped' docs/items/PL-5748-*.md
---

**Problem.** Sweep the open queue for duplicate clusters filed before bin/docket new could warn on a near-duplicate

**The key, and the one that does not work.** `bin/docket new` has never warned
on a near-duplicate (`PL-TZ7T`), so the store has accumulated items describing
one defect two and three times with nothing surfacing them. Title similarity
cannot find them and this is measured rather than assumed: over the 1,362-item
store, title-Jaccard catches **0 of 13** known duplicate pairs at any usable
threshold - 0.45 flags 58 pairs and catches none, and catching 8 needs 0.20,
which flags 768. Known duplicates score 0.121-0.276 against each other because
each session describes the defect from the angle that bit it. The only clusters
it finds cheaply are the items meant to recur - sixteen "Triage the N captures
on DATE", plus release cuts and tags.

**The key that works is `touches` for candidacy and the title only for rank.**
A candidate is another open item sharing at least one declared `touches` path;
candidates are then ranked by Jaccard over title content words. Against
candidate sets of 11 to 57, that puts the true duplicate in the **top 3 for 9
of 9** of the pairs known on 2026-09-20. Taking the union of every item's top 3
gives 400 pairs over 250 of the 341 open items, and it reaches pairs a
threshold never would: `PL-TH7P`/`PL-TZ7T` - the two open items both asking for
the near-duplicate warning itself - score 0.111, well under the 0.18 a
threshold sweep would have used.

**What the key cannot see.** 20 open items declare no `touches` at all, so no
shared path can ever make them a candidate. They were swept separately, by
hand, against an index of all 341 open titles - and that is where `PL-3HMQ`
was found, the third filing of the release-notes/`pr:` defect.

**Method.** Regenerate the pair list with a standard-library script, then read
**both briefs in full** for every pair: whether two items are one defect is
judgment and must not be scripted. Every non-distinct verdict is then put to an
independent reviewer told to refute it, because a false "same finding" destroys
a real finding by dropping it. Per confirmed pair: group under one `feature:`
where they are complementary halves, or drop the weaker with a `reason:` naming
the survivor where they are the same finding. A dropped item's unique evidence
- its measurement, its dated instance - is carried into the survivor's brief
first, so the drop loses nothing.

**Three of one mechanism is not automatically a generator.** `CLAUDE.md`'s
generator rule covers one mechanism causing three or more *distinct* items.
Three filings of one defect is a duplicate cluster, and the remedy is two drops
rather than a `root-cause-of:`. Both shapes occur in this store and they are
recorded differently.
