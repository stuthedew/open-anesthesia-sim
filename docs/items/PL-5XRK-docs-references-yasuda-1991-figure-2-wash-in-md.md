---
id: PL-5XRK
title: docs/references/yasuda-1991-figure-2-wash-in.md: neither Anesth Analg table has a 1.5-minute row, though the protocol sampled at 1.5 minutes and only the Anesthesiology figure is said to plot no point there; say why (copy editor structure read, 2026-11-07)
priority: P2
effort: S
status: ready
classes: defect, docs
feature: references-structure
touches: docs/references/yasuda-1991-figure-2-wash-in.md
added: 2026-11-07
payoff: a reader can tell whether the wash-in values the simulator is tested against cover every point the figure plots
verify: grep -qE '^\| 1\.5 \||The \*Anesth Analg\* figure plots' docs/references/yasuda-1991-figure-2-wash-in.md
---

**Problem.** docs/references/yasuda-1991-figure-2-wash-in.md: neither Anesth Analg table has a 1.5-minute row, though the protocol sampled at 1.5 minutes and only the Anesthesiology figure is said to plot no point there; say why (copy editor structure read, 2026-11-07)

**Checked 2026-11-09:** `grep -n '1\.5' docs/references/yasuda-1991-figure-2-wash-in.md` finds the protocol's sample times, which include 0.75 and 1.5 minutes, and one sentence: "The *Anesthesiology* figure plots no point at 1.5 or 2 minutes." The two *Anesth Analg* tables, sevoflurane and isoflurane from Figure 2 on page 320, have rows at 1, 2, 3, 5, 7.5, 10, 12.5, 15, 20 and 25 minutes, and none at 0.75 or 1.5. The note does not say why. No wrong value was found. If a re-read shows that a point was read at the wrong time, the item becomes a `science` finding at `P1`, because `tests/reference/test_published_wash_in_and_elimination.py` tests the simulator against these values.

**Why it matters.** A reader comparing the tables with the sampling protocol cannot tell whether the figure plots no point at 0.75 and 1.5 minutes or whether points were missed. The simulator is tested against these values, so a missing or mistimed point changes what the test checks.

**Done when.** The *Anesth Analg* Figure 2 page image is read again. The note says, in a sentence beginning "The *Anesth Analg* figure plots", what the figure shows at 0.75 and 1.5 minutes. Or, if the figure plots points there, each table gains its row, read by the note's four steps.

**Generator check.** One-off: a finding from the `docs/references/` structure read (2026-11-07).

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** `git show 817a4d88:docs/references/yasuda-1991-figure-2-wash-in.md` already has the *Anesth Analg* tables with no 1.5-minute row (rows 109 and 124 go from 1 to 2 minutes), and only the *Anesthesiology* figure is said to plot no point there (row 134). So the problem was present at the freeze, commit `817a4d88` (2026-10-24), and this finding belongs on v0.7.0's frozen list rather than deferred.
