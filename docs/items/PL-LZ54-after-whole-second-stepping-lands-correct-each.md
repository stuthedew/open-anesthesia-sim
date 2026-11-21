---
id: PL-LZ54
title: After whole-second stepping lands, correct each passage of docs/INTERFACE.md and docs/ARCHITECTURE.md that PL-5FMC found wrong and left for that build, wherever the build did not rewrite it
status: untriaged
feature: run-computed-one-way
added: 2026-11-21
---

**Problem.** After whole-second stepping lands, correct each passage of docs/INTERFACE.md and docs/ARCHITECTURE.md that PL-5FMC found wrong and left for that build, wherever the build did not rewrite it

**Checked 2026-11-21**, at `2452b9b4e`. `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code) found about 125 passages that state something about the 0.1 s step, the two calculation paths, where a branch opens, or a figure measured under them. It edited none of them, because the whole-second stepping build (`PL-SZ6G`, `PL-MH9J`, `PL-FST0`, `PL-Z6C8`) rewrites them. Ten groups of those passages are wrong against the code today. `PL-5FMC`'s brief lists them under "Wrong today, and left for the whole-second stepping build", with the correction for each, and lists all the passages under "For the whole-second stepping build". The first blind review pass on `PL-5FMC`'s pull request found that nothing in the build's own items points at those lists, so a passage that the build does not rewrite would stay wrong.

Three examples from the first list: "One calculation produces both the caption and the trace, so they cannot disagree" (the caption reads the run's newest state and the trace reads the states that the chart evaluates), "two runs' nearest instants can differ by up to one column" (beside a branch's fork they can differ by up to the hover radius), and "Simulated time is displayed to 0.1 s" (the hover readout prints 0.01 s).

**Why it matters.** `docs/INTERFACE.md` is the authoritative statement of what the interface shows and does. A contributor reads each of these sentences as true.

**Done when.** Each of the ten groups in `PL-5FMC`'s first list is either rewritten by the build or corrected here, each passage in its second list has been read against the code after the build, and this item records the result for each group. This item waits on `PL-Z6C8`, the last item of the build.
