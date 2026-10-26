---
id: PL-TBX9
title: Measure whether bin/docket new's working-tree key records wrong recurrences on open items the filing branch does not claim: after PL-PNSV leaves the claimed item out, the next open item declaring one of the branch's paths becomes the anchor, and PL-PNSV's blind review replayed 50 of 145 recorded recurrences landing on another open item that way; compare withdrawal rates of entries matched on inferred paths and on declared touches
priority: P3
effort: M
status: ready
classes: infra
feature: recurrence-signal
touches: subprojects/docket/src/docket/cli.py, docs/items/PL-TBX9-measure-whether-bin-docket-new-s-working-tree.md
added: 2026-10-25
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

**Generator check.** It is the same mechanism as `PL-PNSV`, at a sibling site.
That fix stopped a capture matching its own branch's item, and the next item
sharing one of the branch's paths takes its place. `PL-PNSV` closed on
2026-10-25, so this is recorded as re-entering it.
