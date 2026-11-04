---
id: PL-2GDW
title: Generator evaluation of the 2026-11-02/03 apparatus burst: record on PL-ZCF9 that the owner-ask wording fact is PL-1ZZ0's family fact, and on PL-9KSJ that its fix should land once in a shared guard entry point sequenced with PL-S3TF
priority: P2
effort: S
status: done
classes: infra
feature: guards-say-when-they-cannot-check
milestone: v0.6.15
touches: docs/items/PL-ZCF9-owner-ask-guard-py-recognises-a-read-or-merge.md, docs/items/PL-9KSJ-every-guard-hook-fails-open-without-a-trace.md
added: 2026-11-03
closed: 2026-11-03
pr: 1994
verify: grep -q '^misread: Which action a request performs' docs/items/PL-ZCF9-owner-ask-guard-py-recognises-a-read-or-merge.md && grep -q 'under .PL-2GDW.' docs/items/PL-9KSJ-every-guard-hook-fails-open-without-a-trace.md
---

**Problem.** The owner asked on 2026-11-03 for the burst of workflow defects filed that day and the day before to be evaluated for generators and root causes. `bin/docket inflow` counted 51 apparatus filings that no head explained when they arrived, plus 10 filed under an open head, in 2026-11-02..11-03: 25.5 a day against 2.7 the week before.

**Evidence.** Grouped by where each filing came from, on 2026-11-03:

1. About 19 came from one review of the guard hooks on 2026-11-03 (feature `guard-review-2026-11`, the heads `PL-1ZZ0` and `PL-9KSJ` and their members).
2. About 10 came from the owner-ask and merge guards refusing messages they should have passed (`PL-0W6J`, `PL-Q0TK`, `PL-VNRM`, `PL-VHMS`, `PL-YN60`, `PL-ZCF9`, `PL-3D2F`, `PL-R1HT`, `PL-L08H`, `PL-NZJG`).
3. About 27 came from work the owner asked for and the first defects found in it: plain-writing review (`PL-H76S` and its fixes), numeric claims in `docs/MODEL.md` held by tests (`PL-B6YV`'s decomposition and the check's first defects), the regular-expression review, the effort trial and dead test limits.
4. The rest were the convergence measurement's own defects (`PL-2T7X`, `PL-NHQ6`, `PL-CJGH`), two network time limits (`PL-TFY2`, `PL-NVT6`), two release cuts and one count written as a word (`PL-RKRG`).

Only groups 1 and 2 point at a mechanism still producing work, and both are in the hook guards.

**Findings.**

1. The owner-ask lineage (`PL-TLPH`, `PL-GPJ7`'s owner-ask re-entries, `PL-ZCF9`, `PL-3D2F`) misread the fact that `PL-1ZZ0` states for the guards: which action a request performs, whatever its text. With `PL-61FT`, that fact has produced 45 items since September. Each head before `PL-1ZZ0` closed spent after covering the spellings or wordings found so far. `PL-ZCF9`'s `misread:` now uses `PL-1ZZ0`'s words, and its brief records the count. No new head was needed.
2. `PL-9KSJ` (guards fail open) and `PL-1ZZ0` differ in the fact misread but share a structure: every guard hand-writes its own payload intake, matching and failure path. `PL-9KSJ`'s brief now recommends that its fix land once, in a shared entry point built under `PL-S3TF`, with a test that refuses a hook not using it.
3. No other group is a generator. The prose-review fixes were iteration on `PL-H76S` (spent). `PL-LPV0` and `PL-5L84` were already recorded against `PL-R417`, `PL-4FBP` and `PL-G424`. The two time-limit items had one fix. The effort-trial pair is one fact with two items.

**Done when.** Both verdicts are written into the briefs of `PL-ZCF9` and `PL-9KSJ`, and `PL-ZCF9`'s `misread:` matches `PL-1ZZ0`'s.

**Generator check.** Bookkeeping: a grooming pass the owner asked for.
