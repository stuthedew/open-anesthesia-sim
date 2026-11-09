---
id: PL-JSBW
title: docs/references/yasuda-1991-anesthesiology-desflurane-isoflurane-halothane-kinetics.md records how the paper derived alveolar ventilation (pages 491, 492, 494) but not what this repository uses those facts for; docs/MODEL.md's dead-space conclusion rests only on the apparatus facts (copy editor structure read, 2026-11-07)
priority: P2
effort: S
status: ready
classes: defect, docs
feature: references-structure
touches: docs/references/yasuda-1991-anesthesiology-desflurane-isoflurane-halothane-kinetics.md
deferred-from: v0.7.0 - a new problem: the note did not exist at the freeze (817a4d88); 0d8ad8f9 (PL-4QCJ, 2026-10-25) created it with its list of uses as written
added: 2026-11-07
payoff: a reader checking the dead-space argument in docs/MODEL.md learns from the note every fact of the paper it rests on
verify: grep -qF '**The ventilation derivation and the clearances.**' docs/references/yasuda-1991-anesthesiology-desflurane-isoflurane-halothane-kinetics.md
---

**Problem.** docs/references/yasuda-1991-anesthesiology-desflurane-isoflurane-halothane-kinetics.md records how the paper derived alveolar ventilation (pages 491, 492, 494) but not what this repository uses those facts for; docs/MODEL.md's dead-space conclusion rests only on the apparatus facts (copy editor structure read, 2026-11-07)

**Checked 2026-11-09:** the note's § "Where this repository uses these facts" lists the four ratios, the recovery values, halothane's 0.25 and the apparatus facts. For `docs/MODEL.md` § "Desflurane's residual, and why the parameter file was not changed", it names only halothane's 0.25 and the apparatus facts. That section uses more. `grep -n 'f_D F_I\|V_1 k_{10}\|f_A \\dot' docs/MODEL.md` finds, in that section, the page 491 formula F_M = f_A F_A + f_D F_I and the page 492 definition V_A = f_A × V_E. It uses these to say that f_A is the alveolar fraction of total minute ventilation. It also finds the page 494 pulmonary elimination clearances, used as a consistency check on the model's 4.0 L/min alveolar ventilation. The note does not list any of these three uses.

**Why it matters.** The note is where a reader finds which of the paper's facts the repository depends on, and where. A reader checking the dead-space argument in `docs/MODEL.md` would not learn from the note that it also rests on the paper's ventilation derivation and clearances.

**Done when.** § "Where this repository uses these facts" has a bullet led "**The ventilation derivation and the clearances.**". It says that `docs/MODEL.md` § "Desflurane's residual, and why the parameter file was not changed" uses the page 491 formula and the page 492 definition to define f_A, and the page 494 clearances as a consistency check on the operating point.

**Generator check.** One-off: a finding from the `docs/references/` structure read (2026-11-07).
