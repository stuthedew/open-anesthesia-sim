---
id: PL-FQFP
title: docs/references/yasuda-1991-anesthesiology-desflurane-isoflurane-halothane-kinetics.md lists page 497 as read on 2026-09-13, but no fact in the note cites it: record what was taken from it, or take it off the reading record (copy editor structure read, 2026-11-07)
priority: P3
effort: S
status: ready
classes: defect, docs
feature: references-structure
touches: docs/references/yasuda-1991-anesthesiology-desflurane-isoflurane-halothane-kinetics.md
deferred-from: v0.7.0 - a new problem: the note did not exist at the freeze (817a4d88); 0d8ad8f9 (PL-4QCJ, 2026-10-25) created it with page 497 in its reading record
added: 2026-11-07
payoff: the recovery values cite the table they were read from, and every page in the note's reading record supports a fact in it
verify: grep -qF 'Table 6, page 497' docs/references/yasuda-1991-anesthesiology-desflurane-isoflurane-halothane-kinetics.md
---

**Problem.** docs/references/yasuda-1991-anesthesiology-desflurane-isoflurane-halothane-kinetics.md lists page 497 as read on 2026-09-13, but no fact in the note cites it: record what was taken from it, or take it off the reading record (copy editor structure read, 2026-11-07)

**Checked 2026-11-09:** `grep -n '497' docs/references/yasuda-1991-anesthesiology-desflurane-isoflurane-halothane-kinetics.md` finds page 497 only in the reading record ("Pages 492, 494 and 497 were read on 2026-09-13"). No fact in the note cites it. `PL-4QCJ`, which made that reading, records what page 497 was read for: "p. 497, Table 6 - recovery: desflurane 105 +/- 25%, isoflurane 102 +/- 13%, halothane 64 +/- 9%". Those are the recovery values the note's table already gives, cited only to the abstract on page 489. So the page was read, and its fact is in the note under another page.

**Why it matters.** A reader checking the recovery values finds them cited only to the abstract, and a reading record that names a page no fact uses. Both make the note harder to check against the paper.

**Done when.** The recovery row of the note's table cites "Abstract, page 489; Table 6, page 497". This is the one correct option, because `PL-4QCJ` recorded that page 497 was read for these values.

**Generator check.** One-off: a finding from the `docs/references/` structure read (2026-11-07).
