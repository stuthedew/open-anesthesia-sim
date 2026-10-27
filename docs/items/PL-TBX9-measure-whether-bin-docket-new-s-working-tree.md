---
id: PL-TBX9
title: Measure whether bin/docket new's working-tree key records wrong recurrences on open items the filing branch does not claim: after PL-PNSV leaves the claimed item out, the next open item declaring one of the branch's paths becomes the anchor, and PL-PNSV's blind review replayed 50 of 145 recorded recurrences landing on another open item that way; compare withdrawal rates of entries matched on inferred paths and on declared touches
priority: P3
effort: M
status: done
classes: infra
feature: recurrence-signal
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/README.md, docs/items/PL-TBX9-measure-whether-bin-docket-new-s-working-tree.md
added: 2026-10-25
closed: 2026-10-27
pr: 1875
payoff: the recurrence count that names generator-tier promotion candidates is known to count the right item, or a fix for it is filed
verify: grep -qE '^\*\*Measured' docs/items/PL-TBX9-*.md
reenters: PL-PNSV
---

**Problem.** Measure whether bin/docket new's working-tree key records wrong recurrences on open items the filing branch does not claim: after PL-PNSV leaves the claimed item out, the next open item declaring one of the branch's paths becomes the anchor, and PL-PNSV's blind review replayed 50 of 145 recorded recurrences landing on another open item that way; compare withdrawal rates of entries matched on inferred paths and on declared touches

**Reproduced 2026-10-26.** `_record_recurrence` in
`subprojects/docket/src/docket/cli.py` writes a filing onto the top-ranked open
item. `PL-PNSV` (merged in #1835) removed only the filing branch's own claimed
item from the candidates. The paths a clean capture infers from the working tree
still choose the next item. `PL-PNSV`'s blind review counted 50 of 145 recorded
recurrences anchored that way.

**Why it matters.** Three recurrences make an item a generator-tier promotion
candidate. A recurrence recorded against the wrong item puts a false candidate
in front of a reader. This over-counts rather than hides a generator, because
a reader confirms each candidate (`PL-X5JR`). So it is not recorded as
impairing generator detection.

**Done when.** This brief carries a `Measured` paragraph, in bold, with the
withdrawal rate of recurrence entries matched on inferred paths and the rate
for those matched on declared `touches`. Where the inferred-path rate is
materially higher, a fix is filed as its own item.

**Measured 2026-10-27.** The inferred-path rate is not materially higher, so
no fix is filed for it. Consider matches on an item that the filing branch
neither claimed nor filed. Sessions withdrew 13 of the 32 matched on inferred
paths (41%, 95% CI 26-58%). They withdrew 15 of the 33 matched on declared
`touches` (45%, 95% CI 30-62%). The two-sided Fisher exact p is 0.80.

**How it was measured.** `origin/main` at `e18218ada` holds 179
`recurrences:` entries, and 79 of them are withdrawn. `PL-4JHS`'s backfill
wrote 13 by hand, so no key chose them. The pull request that filed the
capture wrote the other 166. For each of those, a script read the pull
request's branch (`refs/pull/N/head`) and found the commit that first added
the capture's file. The store the search read is the tree just before that
commit. A capture counts as declaring `touches` when its first committed
version carries them. Otherwise the search used the working-tree paths. Those
are the branch's changes since it forked, plus the filing commit's own changes
in place of the uncommitted ones. The script then found which subject the
capture shared with the matched item. It also checked whether the branch had
claimed that item, by a `Claim:` trailer or its id leading the pull request
title, or had filed it. The script was a one-off and is not kept.

| Key that chose the item | Matched item | Withdrawn |
| --- | --- | --- |
| Inferred path | the branch's own item | 13 of 26 (50%) |
| Inferred path | another open item | 13 of 32 (41%) |
| Declared path | the branch's own item | 11 of 29 (38%) |
| Declared path | an item the same branch filed earlier | 15 of 23 (65%) |
| Declared path | another open item | 15 of 33 (45%) |

The answer survives four checks:

- Counting only the branch's committed changes as the inferred paths, the
  split is 5 of 21 (24%) against 15 of 33 (45%). So it does not rest on the
  stand-in for uncommitted changes.
- A capture's first committed version may carry `touches` added after the
  search ran. Keeping only the 24 declared-path matches that the declared
  paths alone reproduce gives 11 of 24 (46%).
- By period, before `PL-0HLS` widened the key on 2026-10-12, it is 11 of 27
  against 11 of 26. From then until `PL-PNSV`, it is 2 of 5 against 4 of 7.
  None of the six entries dated 2026-10-25 or later is a path match on
  another item.
- 15 of the 166 entries (9%) share no path, item file or cited id with their
  item under today's key. Either the reconstruction or an earlier version of
  the key explains them, and the replay cannot tell which. Seven had inferred
  paths, of which 3 are withdrawn, and eight had declared ones, of which 6
  are withdrawn. Adding them would leave the inferred rate where it is and
  raise the declared one.

A withdrawal measures less than it seems to. The pull request that filed the
capture made 72 of the 79 withdrawals. So the rate is how often the filing
session disowned the match it was shown. An entry still standing is one
nobody disowned, not one shown to be right.

The re-anchoring this item's title describes is rare. Consider the 52 filings
whose matched item the branch claimed in a `Claim:` trailer. With `PL-PNSV`'s
exclusion, the search records nothing for 47 of them. It moves 5 onto another
open item, 4 of them through inferred paths. The blind review's "50 of 145"
is in no file in the repository, including #1835's rows in
`docs/blind-review-findings.tsv`, so it was not reproduced.

One class does stand out: a match on an item that the same branch filed
earlier, withdrawn 15 of 23 times. The session filing both knew the first
existed, so none of them is a recurrence by the definition `PL-PNSV` relies
on. Eight still stand, and two of them make `PL-0889` the only promotion
candidate the digest names. That defect is filed as `PL-8MRM`.

`PL-PNSV`'s own counts do not reproduce. Its Measured paragraph gives 24 of
68 own-item entries withdrawn and 18 of 110 others. The store it measured, at
`e70e84210^`, holds 77 withdrawn entries among its 178. This replay finds the
same 68 own-item entries. At that commit they carry 28 withdrawals, and the
other 110 carry 49. `subprojects/docket/README.md` repeated the 24, and now
gives 28.

**Generator check.** It is the same mechanism as `PL-PNSV`, at a sibling site.
That fix stopped a capture matching its own branch's item, and the next item
sharing one of the branch's paths takes its place. `PL-PNSV` closed on
2026-10-25, so this is recorded as re-entering it.
