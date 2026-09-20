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

**Third-modality result, 2026-09-20: the primary key's blind spot is small.**
The rare-term sweep - pairs sharing three or more rare brief-body terms while
sharing *no* declared `touches:` path, which the primary key cannot reach by
construction - produced 49 pairs. **47 were judged distinct on reading both
briefs, and both of the two non-distinct verdicts were refuted** on independent
adversarial review. Zero confirmed duplicates. So a duplicate pair in this store
reliably declares a shared path, and the `touches` key does not need widening;
what it does need is the separate hand sweep for the items declaring no
`touches` at all, which is where `PL-3HMQ` was found.

The one thing the modality returned was a by-product rather than a duplicate:
`PL-RFSL`, `PL-38PN`'s remainder being refused by
`.claude/rules/citation-drift.md`'s closed-brief clause.

## The sweep's candidate table, externalized

**Read this as candidates, not verdicts, except where the row says otherwise.**
394 of the 400 pairs were read in full; 42 came back non-distinct. Each was
then put to an independent reviewer told to refute it, and *that stage had not
finished when this was written* - the reads and the refutations share a
two-agent concurrency cap, so every read ran before any refutation could start.
`PL-JKML` is written down rather than held in a session precisely so the
refutation stage can be picked up by whoever gets there next.

**Five rows are settled and already applied** (both briefs read by the session
itself, and independently corroborated): `PL-4HKS`/`PL-5748`,
`PL-2M5T`/`PL-W7WL`, `PL-3HMQ`/`PL-W7WL`, `PL-4RHP`/`PL-HCTF` - all dropped
into their survivors above - and `PL-SH9Q`/`PL-KSCW`/`PL-MBTZ`, grouped.

**One row is settled elsewhere and needs nothing**: `PL-5MFL`/`PL-BHBZ` and the
`verify-false-reject` rows around them closed together under `#783` with
`PL-4FD2` and `PL-0KQP`, already carrying that feature.

**Two rows name an item another session holds** and were deliberately not
acted on: `PL-TH7P`/`PL-TZ7T` (the two open items *both* asking for the
near-duplicate warning - a high-confidence same-finding, and the neatest
demonstration in the store of what its absence costs) and anything naming
`PL-X5JR`, `PL-THLT` or `PL-4JHS`, which are live on
`origin/claude/recurrence-signal-feature-3hnynt`.

**Everything else below is unrefuted.** A same-finding row must survive
refutation before anything is dropped on it: a false same-finding destroys a
real finding, which is the one failure this pass cannot take back. A
complementary row is safe to act on sooner, since grouping loses nothing.

| pair | verdict | survivor / feature | conf |
| --- | --- | --- | --- |
| `PL-037Y` / `PL-C7XV` | complementary-halves | `interface-pass-decision-record` | medium |
| `PL-038` / `PL-1T6T` | complementary-halves | `claude-md-context-claims` | medium |
| `PL-1BS2` / `PL-VKGJ` | complementary-halves | `honest-digest-counts` | medium |
| `PL-2M9N` / `PL-8LDF` | complementary-halves | `model-spec-test-binding` | high |
| `PL-3DN1` / `PL-Z85N` | complementary-halves | `unchecked-cut-version` | medium |
| `PL-4FD2` / `PL-5MFL` | complementary-halves | `verify-false-reject` | medium |
| `PL-4FD2` / `PL-BHBZ` | complementary-halves | `verify-false-reject` | medium |
| `PL-4L49` / `PL-HKTB` | complementary-halves | `unmeasured-contrast` | medium |
| `PL-4RHP` / `PL-DHJ7` | complementary-halves | `unchecked-roadmap-counts` | medium |
| `PL-5GBV` / `PL-BGMK` | complementary-halves | `duplicate-item-detection` | medium |
| `PL-5GBV` / `PL-TZ7T` | complementary-halves | `duplicate-title-warning` | high |
| `PL-5MFL` / `PL-STC4` | complementary-halves | `verify-false-reject` | medium |
| `PL-5MFL` / `PL-7K8Y` | complementary-halves | `verify-false-reject` | medium |
| `PL-5N7T` / `PL-WQT0` | complementary-halves | `floor-command-enumeration` | medium |
| `PL-73P0` / `PL-ZPDM` | complementary-halves | `evidence-declines` | medium |
| `PL-BHBZ` / `PL-STC4` | complementary-halves | `verify-false-reject` | medium |
| `PL-BHBZ` / `PL-BX1C` | complementary-halves | `verify-false-reject` | medium |
| `PL-BHBZ` / `PL-ZMGR` | complementary-halves | `verify-false-reject` | medium |
| `PL-BX1C` / `PL-ZMGR` | complementary-halves | `verify-false-reject` | high |
| `PL-BYMX` / `PL-SH9Q` | complementary-halves | `stranded-ahead-or-behind` | medium |
| `PL-CPLX` / `PL-KKRP` | complementary-halves | `freeze-trigger-accuracy` | medium |
| `PL-GJPD` / `PL-QNYF` | complementary-halves | `closure-pr-attribution` | medium |
| `PL-K5PW` / `PL-P757` | complementary-halves | `items-flag-nested-store` | high |
| `PL-KFWL` / `PL-LT77` | complementary-halves | `release-tag-mismatch` | medium |
| `PL-KNHX` / `PL-VJFQ` | complementary-halves | `known-shortfalls-unchecked` | medium |
| `PL-KSCW` / `PL-MBTZ` | complementary-halves | `stranded-ahead-behind` | high |
| `PL-LPWK` / `PL-W7WL` | complementary-halves | `release-note-pr-link` | medium |
| `PL-M21Q` / `PL-NGLM` | complementary-halves | `record-in-item-not-reply` | medium |
| `PL-QNYF` / `PL-WG7Q` | complementary-halves | `carried-work-guard` | medium |
| `PL-R5HK` / `PL-WQT0` | complementary-halves | `architecture-prose-counts` | medium |
| `PL-TKFD` / `PL-ZMGR` | complementary-halves | `falsifies-declaration-route` | medium |
| `PL-W7WL` / `PL-WXX8` | complementary-halves | `cut-backfills-pr-numbers` | high |
| `PL-WNQT` / `PL-X3NY` | complementary-halves | `stranded-false-positive` | medium |
| `PL-1RTM` / `PL-3NKZ` | same-finding | `PL-3NKZ` | high |
| `PL-2M5T` / `PL-W7WL` | same-finding | `PL-2M5T` | high |
| `PL-4HKS` / `PL-5748` | same-finding | `PL-4HKS` | high |
| `PL-4RHP` / `PL-HCTF` | same-finding | `PL-4RHP` | high |
| `PL-5MFL` / `PL-BHBZ` | same-finding | `PL-BHBZ` | high |
| `PL-GXPP` / `PL-R77L` | same-finding | `PL-GXPP` | high |
| `PL-KSCW` / `PL-SH9Q` | same-finding | `PL-KSCW` | high |
| `PL-TH7P` / `PL-TZ7T` | same-finding | `PL-TZ7T` | high |
| `PL-W6NY` / `PL-YRYR` | same-finding | `PL-YRYR` | high |

**What the numbers say about the key itself.** 337 of 378 pairs the key
surfaced were judged distinct on reading, so it runs at roughly one real
signal in ten - which is the right side of the trade for a sweep whose false
negatives are silent and whose false positives cost one brief read.
