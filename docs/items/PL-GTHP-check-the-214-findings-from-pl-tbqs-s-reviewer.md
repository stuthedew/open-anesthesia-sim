---
id: PL-GTHP
title: Check the 214 findings from PL-TBQS's reviewer replay that name no key defect, most of them marked correct at merge by a blind checker, against main, and file what still holds
priority: P2
effort: L
status: done
classes: housekeeping
feature: replay-findings
touches: docs/items
added: 2026-10-24
closed: 2026-10-25
pr: 1830
payoff: every defect the reviewer replay found that still holds on main is queued, instead of lost when the pull request's head can no longer be fetched
verify: grep -qE '^Every finding above is checked against main\.$' docs/items/PL-GTHP-*.md
---

**Problem.** Check the 214 findings from PL-TBQS's reviewer replay that name no key defect, most of them marked correct at merge by a blind checker, against main, and file what still holds

**Where the findings are.** The findings are in `replay/PL-TBQS/findings_by_label.json` at commit `b304302ee`, on `PL-TBQS`'s pull request, under blind labels. `replay/PL-TBQS/labels.json` maps each label to its arm, `scores.json` says which findings named a key defect, and `checks.json` holds the checker's verdict on each. The directory is removed before that pull request merges, so read it from that commit. Of the 269 findings, 55 name a key defect. 2 were marked incorrect and 6 not checkable, so most of the 214 others describe a fault that was real at its merge commit. On `PL-TCBJ`'s ten pull requests they overlap `PL-ZWXD`, which holds that replay's own findings beyond its key, so read that item first and check each fault once.
<!-- absent: replay/PL-TBQS/findings_by_label.json -->
<!-- absent: replay/PL-TBQS/labels.json -->
<!-- absent: scores.json -->
<!-- absent: checks.json -->

**Why it matters.** A blind checker confirmed most of these findings as real at their merge commits. Each one that still reproduces on `main` is a defect that no item records. Many of them are in the simulator's interface, and some may be faults the safety-critical standard covers. The findings exist only on a pull request whose branch is deleted, so the longer they wait, the harder they are to reach.

**How to read them now.** `PL-TBQS`'s branch was deleted when #1750 merged, but GitHub keeps the pull request's head. `git fetch origin pull/1750/head:refs/tmp/pr1750` makes commit `b304302ee` readable, and then `git show b304302ee:replay/PL-TBQS/findings_by_label.json` prints the findings (checked 2026-10-24).

**Done when.** Each of the 214 findings has been checked against `main`. Each one that still reproduces is filed, or named as already covered by an open item, and the brief ends with the line `Every finding above is checked against main.`

**Generator check.** Not owed: the item touches only the queue store. It is a review pass that files findings, not a mechanism.

**Checked 2026-10-25, against `main` at `603b3ebb`.** Five subagents checked the 214 findings, five pull requests each at most, by reading the current code and reproducing where a script could. Several reviewers often described one fault, so the 214 findings and `PL-ZWXD`'s 24 entries reduce to 106 distinct faults. By finding: 95 still hold, 92 are fixed, 16 are already recorded by an open item (`PL-06LS`, `PL-88MK`, `PL-DP7B`, `PL-HSP8`, `PL-QG52`, `PL-YH6Z`), 5 describe code that is gone, and 6 are not defects. The faults that hold, `PL-ZWXD`'s entries included, are 44, filed as 43 items under `replay-findings`, `mac-awake-reference-text`, `supported-run-length-text` and `area-layout-sizing`; two faults in one paragraph of the 24-hour argument share `PL-MLPT`. The 32 filed items that carry a debt class join v0.7.0's frozen list, because each fault existed when the gate froze, as the earlier replay findings did.

The ledger below gives each finding's verdict, by pull request and by its blind label from `replay/PL-TBQS/findings_by_label.json` at `b304302ee`. "Fixed" names the item that fixed it where the checker found one.

- `#204`: r01 F1 covered by `PL-QG52`; r01 F3 half fixed, half filed as `PL-HF4B`; r02 F1 fixed (`PL-7DJK`); r02 F2 filed as `PL-HF4B`; r03 F1 filed as `PL-HF4B`; r03 F2 fixed (`PL-7DJK`); r04 F1 covered by `PL-QG52`; r04 F2 filed as `PL-HF4B`; r04 F3 code gone; r05 F1 filed as `PL-HF4B`; r05 F2 code gone; r05 F3 fixed (`PL-7DJK`); r06 F1 filed as `PL-3B34`; r06 F2 filed as `PL-HF4B`; r06 F3 covered by `PL-QG52`; r06 F4 fixed (`PL-7DJK`).
- `#288`: r01 F1 fixed (`PL-G59B`); r01 F2 filed as `PL-02CD`; r01 F3 filed as `PL-WRVX`; r02 F2 filed as `PL-02CD`; r02 F3 fixed; r03 F2 filed as `PL-6W49`; r03 F3 code gone; r04 F1 filed as `PL-GCGX`; r04 F2 filed as `PL-YDRT`; r04 F3 filed as `PL-39KH`; r05 F1 filed as `PL-02CD`; r05 F2 filed as `PL-GT8W`; r05 F3 fixed; r05 F4 filed as `PL-YDRT`; r06 F1 filed as `PL-6W49`; r06 F3 filed as `PL-02CD`.
- `#331`: r01 F1 fixed (`PL-SQJ1`); r01 F2 filed as `PL-X4X2`; r01 F3 fixed; r02 F1 fixed; r02 F2 fixed (`PL-2FM6`); r02 F3 filed as `PL-X4X2`; r02 F4 fixed; r03 F1 code gone; r03 F2 code gone; r03 F3 fixed; r03 F4 filed as `PL-X4X2`; r03 F5 fixed; r04 F1 fixed; r04 F2 fixed; r04 F3 not a defect; r05 F1 fixed; r05 F2 fixed; r05 F3 fixed; r06 F2 fixed; r06 F3 filed as `PL-X4X2`; r06 F4 fixed (`PL-NWTM`); r06 F5 fixed.
- `#376`: r01 F1 filed as `PL-N559`; r02 F1 filed as `PL-DQL9`; r02 F2 filed as `PL-5RPD`; r03 F1 filed as `PL-PM67`; r03 F2 filed as `PL-ZPY5`; r04 F1 fixed (`PL-HQF5`); r04 F2 covered by `PL-DP7B`; r04 F3 fixed (`PL-X9KD`); r05 F1 fixed (`PL-YZ17`); r05 F2 filed as `PL-PM67`; r06 F1 filed as `PL-DQL9`; r06 F2 covered.
- `#421`: r01 F1 filed as `PL-MLPT`; r01 F2 filed as `PL-KHXB`; r01 F3 fixed (`PL-YZ17`); r01 F4 fixed; r02 F1 fixed (`PL-YZ17`); r03 F1 filed as `PL-MLPT`; r03 F2 filed as `PL-KHXB`; r03 F3 fixed; r04 F1 filed as `PL-0889`; r04 F2 filed as `PL-3B34`; r04 F3 filed as `PL-KHXB`; r05 F1 filed as `PL-MLPT`; r05 F2 fixed (`PL-5291`); r06 F1 filed as `PL-MLPT`; r06 F2 filed as `PL-KHXB`; r06 F3 filed as `PL-MLPT`.
- `#430`: r01 F1 fixed (`PL-2FM6`); r01 F2 fixed (`PL-2FM6`); r01 F3 fixed (`PL-TFX5`); r02 F1 filed as `PL-9SL5`; r02 F2 fixed; r03 F1 fixed (`PL-CNCF`); r03 F2 fixed (`PL-VCP4`); r03 F3 fixed; r04 F1 fixed; r04 F2 fixed (`PL-2FM6`); r05 F1 fixed (`PL-CN5S`); r05 F2 filed as `PL-0WFJ`; r05 F3 fixed (`PL-TFX5`); r05 F4 not a defect; r06 F1 filed as `PL-9SL5`; r06 F2 covered by `PL-06LS`; r06 F3 fixed (`PL-TFX5`).
- `#568`: r01 F1 fixed (`PL-ZMRT`); r01 F2 filed as `PL-NRR6`; r02 F1 filed as `PL-K5BS`; r03 F1 filed as `PL-K5BS`; r03 F2 fixed (`PL-TFX5`); r03 F3 fixed; r04 F1 filed as `PL-K5BS`; r04 F2 fixed; r04 F3 fixed; r04 F4 fixed (`PL-5291`); r05 F1 filed as `PL-VHQX`; r05 F2 filed as `PL-K5BS`; r05 F3 not a defect; r05 F4 fixed (`PL-7TBQ`); r06 F1 filed as `PL-K5BS`.
- `#578`: r01 F1 covered by `PL-88MK`; r01 F2 covered by `PL-YH6Z`; r01 F4 fixed (`PL-25KS`); r02 F1 covered by `PL-88MK`; r03 F1 covered by `PL-YH6Z`; r03 F3 filed as `PL-CJJ1`; r03 F4 filed as `PL-T5NJ`; r04 F1 covered by `PL-YH6Z`; r04 F2 filed as `PL-T5NJ`; r04 F3 filed as `PL-CJJ1`; r05 F1 covered by `PL-88MK`; r05 F3 filed as `PL-CJJ1`; r05 F4 filed as `PL-T5NJ`; r06 F2 filed as `PL-T5NJ`.
- `#775`: r01 F1 fixed (`PL-T995`); r01 F2 filed as `PL-QBQX`; r02 F1 fixed; r02 F4 filed as `PL-QBQX`; r03 F1 fixed; r03 F3 filed as `PL-QBQX`; r04 F2 fixed (`PL-3K9B`); r04 F3 filed as `PL-M8F6`; r05 F1 fixed; r05 F2 filed as `PL-QBQX`; r06 F1 fixed; r06 F3 filed as `PL-QBQX`.
- `#784`: r01 F3 fixed (`PL-MMNX`); r01 F4 not a defect; r02 F1 filed as `PL-TNYP`; r02 F3 fixed (`PL-Y2SL`); r03 F2 fixed; r04 F2 filed as `PL-TNYP`; r05 F1 fixed (`PL-LHBY`); r05 F2 fixed; r05 F3 fixed; r06 F4 fixed.
- `#805`: r01 F1 fixed (`PL-4KZD`); r01 F3 fixed (`PL-1ZQ4`); r02 F3 filed as `PL-XV0D`; r03 F2 fixed (`PL-1ZQ4`); r04 F2 fixed; r05 F2 filed as `PL-XV0D`; r06 F1 fixed; r06 F2 fixed.
- `#1292`: r01 F1 fixed (`PL-8H2R`); r02 F1 fixed (`PL-5291`); r02 F2 fixed; r02 F3 fixed (`PL-5F76`); r03 F1 fixed (`PL-CN5S`); r04 F1 fixed; r06 F1 fixed; r06 F2 fixed.
- `#1328`: r01 F1 not a defect; r03 F1 filed as `PL-CJYL`; r05 F2 fixed (`PL-3800`).
- `#1350`: r02 F1 filed as `PL-S11T`; r02 F2 fixed (`PL-LBQY`); r02 F3 fixed (`PL-LLMN`); r03 F1 fixed; r03 F2 fixed; r04 F1 filed as `PL-S11T`.
- `#1365`: r05 F1 fixed (`PL-7DJK`); r05 F2 fixed (`PL-7DJK`).
- `#1448`: r01 F1 fixed (`PL-391Y`); r01 F2 fixed (`PL-TH35`); r03 F1 fixed; r03 F2 not a defect; r04 F1 fixed; r06 F1 fixed.
- `#1451`: r01 F1 covered by `PL-HSP8`; r01 F2 filed as `PL-3JTH`; r02 F1 covered by `PL-HSP8`; r04 F1 covered by `PL-HSP8`; r05 F1 covered by `PL-HSP8`; r05 F2 fixed (`PL-2N43`).
- `#1585`: r01 F1 filed as `PL-HF1B`; r01 F2 filed as `PL-6XPZ`; r02 F1 fixed (`PL-NNML`); r02 F2 filed as `PL-HF1B`; r02 F3 filed as `PL-VFPB`; r03 F1 filed as `PL-6RJ0`; r03 F2 filed as `PL-HF1B`; r03 F3 filed as `PL-KDZW`; r04 F1 filed as `PL-HF1B`; r04 F2 fixed (`PL-F2YS`); r04 F3 filed as `PL-M4WT`; r05 F1 filed as `PL-HF1B`; r05 F2 filed as `PL-KDZW`; r06 F1 filed as `PL-M4WT`; r06 F2 filed as `PL-6RJ0`.
- `#1622`: r01 F2 filed as `PL-Y65Q`; r02 F2 filed as `PL-QZ7Z`; r02 F3 filed as `PL-97WX`; r02 F4 filed as `PL-C9XP`; r03 F2 filed as `PL-C9XP`; r03 F3 filed as `PL-QZ7Z`; r05 F2 filed as `PL-QZ7Z`; r05 F3 filed as `PL-C9XP`; r06 F2 filed as `PL-QZ7Z`; r06 F3 filed as `PL-C9XP`.

Every finding above is checked against main.
