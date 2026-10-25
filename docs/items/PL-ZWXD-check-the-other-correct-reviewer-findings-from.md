---
id: PL-ZWXD
title: Check the other correct reviewer findings from PL-TCBJ's replay against main and file each one that still reproduces
priority: P2
effort: M
status: done
classes: housekeeping
feature: replay-findings
touches: docs/items
added: 2026-10-24
closed: 2026-10-25
pr: 1830
payoff: every still-present defect a blind checker confirmed in the replay is queued, instead of lost with the session that found it
verify: grep -qE '^Every entry above is checked against main\.$' docs/items/PL-ZWXD-*.md
---

**Problem.** Check the other correct reviewer findings from PL-TCBJ's replay against main and file each one that still reproduces

**What to check.** `PL-TCBJ`'s replay produced 62 panel findings, of which a blind checker marked 59 correct at their merge commits. Four are filed as `PL-HSP8`, `PL-88MK`, `PL-YH6Z` and `PL-QG52`. Most of the rest describe code that later changed, so each needs checking against `main` before it is filed. The findings text lived in the session's scratchpad and is gone. This list keeps enough to find each one again; the number after each is how many of the six reviewers on that pull request raised it (three panel, two generalist runs, counting the discarded one).

- `#1585` (record column band): the control-change record is clipped at the height of the run rows, so the "earlier change(s) not listed" note falls out of view (4); unconditional values scroll out of view after a fork, and `isVisible()` cannot tell (2); readout sections in a compared case do not name their run (1); the "1 MAC" line is rewritten by a halt while the cards keep the last frame (1); the "Delivered" setting sits under "Model outputs" and may read as one (2, not checkable).
- `#775` (bookmark halts): a halt on a mark is never drawn, which `PL-T995` fixed; nothing names the mark that stopped the run, and a second halt on a target already "reached" looks like a plain pause (4); `docs/MODEL.md` says the halt shows the marked height, but it lands up to one step past it (1).
- `#204` (step atomicity): the accounting panel reads "Valid" under a banner that says accounting failed (3); the banner says a step was rolled back even when the render loop failed (4); `docs/MODEL.md` says a halted run cannot step on, though it can once the setting is reverted (2).
- `#578` (Qt chart): the 1.05 terminus ceiling drops the crossing column at long time bases, so the wash-in stretch ends with no terminus (4); the hover labels a column with an instant rounded to 0.1 s while showing the state at the unrounded instant (4); a legend row cannot wrap (1); `drift.yml` lacks the `libegl1` install that `quality.yml` gained (1).
- `#1350` (flow types): a protocol 0 or 1 pickle rebuilds a flow without its guard (3).
- `#1292` (run-length guards): a state standing exactly on 24:00:00 shows "Paused" with Start enabled until a refused step (1); `advance_to` has no bound on reach (1).
- `#331` (playback, in Flet code the Qt port replaced): the tick sleeps after each burst, so 300x plays at about 270x (4); run history grows about 1.3 GB per wall-clock hour at 300x (3); the rate line still reads "300x" while paused (3); a rate refusal outside the `try` would end the tick loop (4); a modal dialog does not pause the run (1). Check whether the Qt port carries each.
- `#1451` (mark branches): refusal messages name methods and raw seconds rather than formatted instants (1).

**Why it matters.** Most of the 59 findings a blind checker marked correct were never filed. Some describe what a learner sees, such as an accounting panel reading "Valid" under a banner saying accounting failed, so each one still present is a misleading display nobody has queued.

**Generator check.** Work the owner asked for: it finishes filing `PL-TCBJ`'s replay, which the owner requested.

**Done when.** Each entry above is checked against `main` and either filed as its own item or recorded here as fixed or not reproducing, and the brief ends with the line "Every entry above is checked against main."

**Checked 2026-10-25, against `main` at `603b3ebb`, by `PL-GTHP`.** `PL-TBQS`'s replay reviewed the same pull requests, so `PL-GTHP` checked each entry above alongside its own findings, once per fault. Numbering follows the order of the entries under each pull request above. Of the 24 entries, 11 still hold and are filed, 12 are fixed, and 1 describes code that is gone. The fixed entry for `#775`'s undrawn halt is `PL-T995`, as the list says.

- `#204`: ZWXD-1 filed as `PL-HF4B`; ZWXD-2 fixed; ZWXD-3 code gone.
- `#331`: ZWXD-1 fixed; ZWXD-2 fixed; ZWXD-3 filed as `PL-X4X2`; ZWXD-4 fixed; ZWXD-5 filed as `PL-TPBH`.
- `#578`: ZWXD-1 filed as `PL-CJJ1`; ZWXD-2 filed as `PL-T5NJ`; ZWXD-3 fixed; ZWXD-4 fixed (`PL-FPCK`).
- `#775`: ZWXD-1 fixed (`PL-T995`); ZWXD-2 filed as `PL-QBQX`; ZWXD-3 filed as `PL-M8F6`.
- `#1292`: ZWXD-1 fixed; ZWXD-2 fixed.
- `#1350`: ZWXD-1 fixed (`PL-5D1Z`).
- `#1451`: ZWXD-1 filed as `PL-3JTH`.
- `#1585`: ZWXD-1 filed as `PL-HF1B`; ZWXD-2 fixed; ZWXD-3 fixed; ZWXD-4 filed as `PL-6RJ0`; ZWXD-5 filed as `PL-M4WT`.

Every entry above is checked against main.
