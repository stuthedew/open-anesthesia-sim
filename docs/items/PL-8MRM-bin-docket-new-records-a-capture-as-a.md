---
id: PL-8MRM
title: bin/docket new records a capture as a recurrence of an item the same branch filed earlier, though the session filing both knew the first existed: 15 of 23 such entries were withdrawn, and the 8 still standing include the two that make PL-0889, three items #1830 filed together under one feature, the only promotion candidate the digest names
priority: P1
effort: S
status: done
classes: defect
feature: recurrence-signal
milestone: v0.6.9
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, docs/items/PL-0TD9-bin-docket-claim-and-yield-write-the-claim-and.md, docs/items/PL-8MHZ-yaml-scalar-and-line-grammar-is-respelt-outside.md, docs/items/PL-9NZ3-six-more-tools-read-the-python-files-on-disk.md, docs/items/PL-KHXB-the-banner-shown-when-a-run-reaches-the-24-hour.md, docs/items/PL-MLPT-docs-model-md-and-core-supported-ranges-py.md, docs/items/PL-NRR6-a-branch-can-be-taken-at-the-keyframe-where-the.md, docs/items/PL-Y65Q-an-area-too-small-for-its-view-is-held-at-a.md, docs/items/PL-YHR3-with-every-frame-failing-the-bookmark-panel.md, subprojects/docket/tests/test_vcs_silence.py
deferred-from: v0.7.0 - captured after the freeze by PL-TBX9's measurement; the generator tier ranks it, not the gate
added: 2026-10-27
closed: 2026-10-27
pr: 1879
payoff: A batch of related findings filed by one session no longer counts as a defect firing again, so the promotion candidates bin/docket next names rest only on filings by sessions that did not know the item existed
verify: grep -q 'def test_new_records_nothing_on_an_item_this_branch_filed' subprojects/docket/tests/test_cli.py
impairs-generators: docket.cli.cmd_new records a recurrence on an item the filing branch itself added, through duplicates.near_duplicates' declared-touches key, so plan.recurrence_chains counts filings by a session that knew the item existed toward the promotion floor and names PL-0889 as a candidate on two such entries
reenters: PL-PNSV
---

**Problem.** bin/docket new records a capture as a recurrence of an item the same branch filed earlier, though the session filing both knew the first existed: 15 of 23 such entries were withdrawn, and the 8 still standing include the two that make PL-0889, three items #1830 filed together under one feature, the only promotion candidate the digest names

**Reproduced 2026-10-27.** `PL-TBX9` replayed the 166 `recurrences:`
entries that `bin/docket new` wrote, against the branch and the store each
capture was filed from. In 23 of them, the matched item had been filed
earlier on the same branch, in the same commit or an earlier one. All 23 were
matches on a declared `touches` path. A session files several findings with
one `--touches` value, and each capture after the first matches the ones
before it. Sessions withdrew 15 of the 23 (65%). That is the highest rate of
any class: matches on other items were withdrawn 41% to 45% of the time.
`PL-PNSV`'s exclusion does not reach these entries. It reads only the items
the branch claims, and nobody claims a capture that was filed a minute ago.

The eight entries still standing, each a capture recorded on an item its own
branch filed:

- `PL-DDYD` on `PL-0TD9`, #981
- `PL-4DK2` on `PL-8MHZ`, #1425
- `PL-8W1J` on `PL-9NZ3`, #1425
- `PL-0889` on `PL-KHXB`, #1830
- `PL-KHXB` on `PL-MLPT`, #1830
- `PL-TNYP` on `PL-NRR6`, #1830
- `PL-C9XP` on `PL-Y65Q`, #1830
- `PL-5JTH` on `PL-YHR3`, #1492

**Why it matters.** `plan.recurring` defines a recurrence as a filing by a
session that hit the defect without knowing the item existed. A session that
filed the item minutes earlier knew it existed. Two of the eight entries,
`PL-0889` on `PL-KHXB` and `PL-KHXB` on `PL-MLPT`, form the chain that makes
`PL-0889` the one item the digest's "Filed more than once" line names. #1830
filed all three under the feature `supported-run-length-text`, because its
session knew they were one group. A false entry also attracts later filings,
because `duplicates.anchor` prefers a candidate that already carries live
recurrences (`PL-34BG`).

**Done when.** `bin/docket new` neither prints nor records, as a possible
earlier filing, an item whose file this branch added. That covers files
committed since the default branch and files not yet committed. A test in
`subprojects/docket/tests/test_cli.py` files two captures on one branch with
one `--touches` value, and shows that nothing is recorded on the first. The
eight entries above are withdrawn with `bin/docket withdraw <item> <capture>
--because PL-8MRM`. `subprojects/docket/README.md` § "Capture costs nothing"
states the exclusion beside `PL-PNSV`'s, and why. `PL-NRR6` is in flight on
another branch, so withdraw its entry after that branch merges, or resolve the
one-line conflict.

**Recommendation.** Exclude an item whose file the branch added. Read that
list in `vcs.py` beside `working_paths`, as `claims.claimed_here` reads the
claims. This is `PL-PNSV`'s own principle, a session that knew the item
existed, applied to the second way a session knows one. The alternative is to
stop counting a match where the capture and the item share a feature. That
rule catches all eight standing entries, but only 18 of the 23, and it would
also drop a match by a later session that only reused the feature's name.

**Generator check.** The fact misread is whether the session filing a capture
already knew the matched item existed. `PL-PNSV` read that fact from the
branch's claims. An item the branch filed is the same fact at a sibling site.
`PL-PNSV` closed on 2026-10-25, within 30 days, so this re-enters it. It is the
second item to re-enter `PL-PNSV`, after `PL-TBX9`, so no generator is owed
yet. A third would make `PL-PNSV` a generator whose fix did not hold.
