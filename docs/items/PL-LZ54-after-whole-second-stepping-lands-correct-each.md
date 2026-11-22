---
id: PL-LZ54
title: After whole-second stepping lands, correct each passage of docs/INTERFACE.md and docs/ARCHITECTURE.md that PL-5FMC found wrong and left for that build, wherever the build did not rewrite it
priority: P2
effort: M
status: ready
classes: defect, docs
feature: run-computed-one-way
touches: docs/INTERFACE.md, docs/ARCHITECTURE.md
blocked-by: PL-Z6C8
deferred-from: v0.7.0 - a new problem: the passages describe the 0.1 s step and the chart as they were before work done after the freeze, the whole-second stepping build (#2180, d4e8200c) among it, and PL-5FMC (#2181) listed them
added: 2026-11-21
payoff: A contributor reading the interface specification about the step, the chart and branching reads what the code now does, not what the 0.1 s step did.
---

**Problem.** After whole-second stepping lands, correct each passage of docs/INTERFACE.md and docs/ARCHITECTURE.md that PL-5FMC found wrong and left for that build, wherever the build did not rewrite it

**Checked 2026-11-21**, at `2452b9b4e`. `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code) found about 125 passages that state something about the 0.1 s step, the two calculation paths, where a branch opens, or a figure measured under them. It edited none of them, because the whole-second stepping build (`PL-SZ6G`, `PL-MH9J`, `PL-FST0`, `PL-Z6C8`) rewrites them. Ten groups of those passages are wrong against the code today. `PL-5FMC`'s brief lists them under "Wrong today, and left for the whole-second stepping build", with the correction for each, and lists all the passages under "For the whole-second stepping build". The first blind review pass on `PL-5FMC`'s pull request found that nothing in the build's own items points at those lists, so a passage that the build does not rewrite would stay wrong.

Three examples from the first list: "One calculation produces both the caption and the trace, so they cannot disagree" (the caption reads the run's newest state and the trace reads the states that the chart evaluates), "two runs' nearest instants can differ by up to one column" (beside a branch's fork they can differ by up to the hover radius), and "Simulated time is displayed to 0.1 s" (the hover readout prints 0.01 s).

**Why it matters.** `docs/INTERFACE.md` is the authoritative statement of what the interface shows and does. A contributor reads each of these sentences as true.

**Done when.** Each of the ten groups in `PL-5FMC`'s first list is either rewritten by the build or corrected here, each passage in its second list has been read against the code after the build, and this item records the result for each group.

[superseded 2026-11-21: `PL-Z6C8` closed with the build in #2180] This item waits on `PL-Z6C8`, the last item of the build.

**Checked 2026-11-21:** the build landed in pull request 2180. It rewrote `docs/INTERFACE.md` § "Halting on a marked crossing", the two sections on how a run is stored and how branches reproduce (now § "A run stores the state of every second it reaches" and § "Each second has one stored state"), § "The shared history is identical by construction, not by measurement" and the preview's developer note, and `docs/ARCHITECTURE.md`'s sections on the run record and on branching. The other passages in `PL-5FMC`'s two lists are still this item's to read against the code.

**Checked 2026-11-22**, at `d4e8200c`, after the build merged. At least two of
the ten groups are still wrong. `grep -n 'cannot disagree' docs/INTERFACE.md`
printed line 3466, the end of "One calculation produces both the caption and
the trace, so they cannot disagree" (group 5). `grep -n 'every 4 s' docs/INTERFACE.md`
printed line 5091, which gives the column spacing for a 60-minute axis without
saying it holds only on a plot 900 px wide (group 4). Group 1, the figures for
comparing two readouts, is also the subject of `PL-VM4Q` (the reversal bound
and the largest differential in those paragraphs), so whichever item is worked
first should take both. At the Gate 3 freeze (`0947408`) a run stepped every 0.1 s
(`SIMULATION_STEP_S: Final = SimulationStep(0.1)` in `app/dashboard_frame.py`),
which is the step these passages describe.

**Generator check.** The fact is the link between a document sentence and the
tree fact it restates, which `PL-BLN0` and its family state. This item is the
planned remainder of `PL-5FMC`'s sweep, left for a build that rewrote the same
passages, so it is bookkeeping and not a re-entry.
