---
id: PL-FM15
title: PL-4FBP (the link between a document sentence and the tree fact it restates) is re-entered by PL-LNFG, PL-D1LR and PL-PTDZ: decide whether a successor head is owed, and whether the docs/MODEL.md items about figures the model computes and the restated display resolution share one misread fact
priority: P2
effort: S
status: untriaged
classes: housekeeping
feature: generator-heads
touches: docs/items
added: 2026-10-31
payoff: bin/docket inflow lists PL-4FBP's line as answered with the reason recorded, instead of re-asking it every run
verify: bin/docket inflow --lane product | grep -A2 'no successor owed' | grep -q 'PL-4FBP'
no-successor: PL-4FBP
---

**Generator check.** One-off. This item records a decision about
`PL-4FBP`'s line and does not misread a fact itself.

**Problem.** PL-4FBP (the link between a document sentence and the tree fact it restates) is re-entered by PL-LNFG, PL-D1LR and PL-PTDZ: decide whether a successor head is owed, and whether the docs/MODEL.md items about figures the model computes and the restated display resolution share one misread fact

The project owner asked for this on 2026-10-31, after `PL-R4Y2`'s triage put
the `reenters:` records on `PL-D1LR` and `PL-PTDZ`. This was read on `main`
after `#1888` merged.

**Answer: no successor head is owed, and the six items do not share one
misread fact.** This is a session's decision, delegated by the owner's request,
so ordinary evidence reopens it. The field `no-successor: PL-4FBP` records it.
The line opens again once three more filings re-enter `PL-4FBP` after
2026-10-31.

**What each of the six misread.** Two items have `PL-4FBP`'s fact, and four
do not.

- `PL-D1LR` (the six-decimals sentences) has `PL-4FBP`'s fact. The document
  already holds the panel's 0.1 L resolution once, in § "Displayed
  precision", and the code holds it in `_RUN_TOTAL_LITRE_DECIMALS` in
  `src/anesthesia_sim/app/formatting.py`. The sentences restate the value
  instead of citing the section. Clause 1 of `PL-4FBP` already covers this
  case, so the repair is to cite the section.
- `PL-PTDZ` (the MAC-awake washout figures) has `PL-4FBP`'s fact, for a
  figure that comes from a simulation run. Its `derived:` marker names two of
  the figure's inputs. The figure also depends on the coefficients, volumes,
  flows and protocol, which no marker can list. The paragraph says "measured
  on 2026-10-26", so clause 4 of `PL-4FBP` treats it as a dated record. That
  boundary was drawn on purpose. `PL-PTDZ` asks for a test because a learner
  still reads the figure as what the model does now.
- `PL-39KH`, `PL-MLPT`, `PL-M8F6` and `PL-5RPD` do not have `PL-4FBP`'s
  fact. Each sentence was false when it was written, and the tree never moved
  past it. They came from `#288`, `#376`, `#421` and `#775`, merged between
  2026-09-03 and 2026-09-20, and `PL-TBQS`'s replay of those pull requests
  found them. A link only says which entity holds a sentence, so it cannot
  catch a sentence that was wrong from the start. The four misread three
  different properties of the model. `PL-39KH` misread uptake: at a 1 MAC
  dial, muscle and fat uptake keep the alveolar fraction below 1 MAC.
  `PL-MLPT` misread exposure: the cap limits elapsed time, and MAC-hours
  count concentration times time. `PL-M8F6` and `PL-5RPD` both misread the
  step: a setting holds for a whole step, and a crossing is found at the end
  of the step that crosses it. `PL-R4Y2`'s pass of 2026-10-26 listed these
  four under `PL-4FBP`. The same paragraph called the
  `mac-awake-reference-text` and `supported-run-length-text` items one-offs
  that misread a source or the model's physiology. This reading keeps the
  second verdict.

**Why the three re-entries do not show `PL-4FBP`'s fix failing.**

- `PL-LNFG` (citations in a data file's `note`) is a part of `PL-4FBP`'s own
  fix that is not done yet. `PL-4FBP`'s disposition table re-scoped `PL-DBGT`
  so that `check_citations` would reach the notes. `PL-LNFG` was split out of
  `PL-DBGT` to do that, and it waited behind the generator pause until
  2026-10-11.
- `PL-D1LR`'s sentences were written on 2026-09-07 in `#435`. They went stale
  when `PL-TG60` (`#588`) changed the panel to 0.1 L on 2026-09-15, four days
  before `PL-4FBP` closed. Nobody found the stale value until 2026-10-25, the
  day the plain-English rewrite (`#1808`) carried it forward.
- `PL-PTDZ`'s figures are not stale. The item guards against a future
  parameter change, at the boundary that clause 4 draws.

`PL-R4Y2` also listed 28 items with `PL-4FBP`'s fact that are not recorded as
its members: the 27 from 2026-10-25 and `PL-3HT2`. 24 of them were filed
before `PL-4FBP` closed on 2026-09-19. Three of the other four are code
docstrings or messages, which are outside the documents that `PL-4FBP`'s
convention binds: `PL-01GY`, `PL-RBMK` and `PL-3HT2`. The fourth, `PL-1QL6`,
names a method that `PL-GS5X` removed on 2026-09-05. So the mechanism produced
about 24 items in the three weeks before the close. Since the close, the
documents the convention binds have produced one new instance, `PL-PTDZ`, at
a boundary drawn on purpose. No mechanism with three members is left for a
successor head to fix, and each re-entry already has its own repair item.

**Leads, not heads.** Two items, `PL-M8F6` and `PL-5RPD`, misread what a step
does to an event. A third would make that a generator, and no head's
`misread:` states the fact today. `PL-PTDZ` is the only item that asks whether
a dated simulation figure in `docs/MODEL.md` should be held by a test. A
second figure of that kind found stale would reopen clause 4 for that kind of
sentence.
