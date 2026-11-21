---
id: PL-FST0
title: Open a branch at any whole second by copying its parent's stored states up to that second
status: untriaged
feature: run-computed-one-way
added: 2026-11-21
---

**Problem.** Open a branch at any whole second by copying its parent's stored states up to that second

**Why it matters.** A branch can open today only where the run's definition holds a keyframe, which three closed items worked around (`PL-B8MK`, `PL-W4XQ`, `PL-Y2SL`). The owner chose this design on 2026-11-21 in `PL-7CY5` (one rule for computing a run), which holds the counts, the measurements and the sources. The four items of the feature `run-computed-one-way` are built in this order: `PL-SZ6G`, `PL-MH9J`, `PL-FST0`, `PL-Z6C8`.

**What it changes.** A branch opened at second n holds its parent's stored states for seconds 0 to n and steps on from there. A learner can branch at any whole second of a run.

**Done when.** A branch opens at any whole second, and a test shows that the branch's stored states equal its parent's, bit for bit, up to and including that second.
