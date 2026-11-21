---
id: PL-MH9J
title: Store every second's state of a run in one array, and have the chart, the readouts, the marks, the wash-in label and the export read that array
status: untriaged
feature: run-computed-one-way
added: 2026-11-21
---

**Problem.** Store every second's state of a run in one array, and have the chart, the readouts, the marks, the wash-in label and the export read that array

**Why it matters.** Today a run's states are computed on demand by three routes: the stepped system, `RunDefinition.state_at` and the display's `evaluate` and `evaluate_anchored`. They agree only to rounding, so each comparison between them needs an allowance, and a MAC target once read as reached on the trunk and not on a branch opened at the same step (`PL-QVBR`). The owner chose this design on 2026-11-21 in `PL-7CY5` (one rule for computing a run), which holds the counts, the measurements and the sources. The four items of the feature `run-computed-one-way` are built in this order: `PL-SZ6G`, `PL-MH9J`, `PL-FST0`, `PL-Z6C8`.

**What it changes.** Each step appends its state to one array for the run, nine numbers per second for one agent, about 6.2 MB over 24 hours. The chart, the readouts, the marks and MAC targets, the wash-in label and the export read that array and nothing else. Nothing draws an interpolated value between two stored seconds, because that would be a second route to a displayed number. `.claude/rules/run-is-its-definition.md` is rewritten in the same pull request, because it forbids exactly this store.

**Done when.** Every displayed or exported state is read from the stored array, and a test shows that the chart, the readouts and the marks read the same stored state for each second.
