---
id: PL-NQWX
title: docs/MODEL.md § 'Independent-solution test' uses 'the operator split', the earlier approximate method, and no chapter says what it was or when the exact step replaced it (copy editor structure read, 2026-11-05)
priority: P3
effort: S
status: ready
classes: docs
feature: model-md-structure
touches: docs/MODEL.md
deferred-from: v0.7.0 - not present at the freeze (817a4d88): 7ca66f0b (#1947) removed the operator split's explanation and left the term
added: 2026-11-05
payoff: a developer reading why the independent-solution limit does not shrink with the step learns what the earlier method was and that the code no longer uses it
verify: ! grep -qF 'operator split, had an error proportional to the step' docs/MODEL.md
---

**Problem.** docs/MODEL.md § 'Independent-solution test' uses 'the operator split', the earlier approximate method, and no chapter says what it was or when the exact step replaced it (copy editor structure read, 2026-11-05)

**Checked 2026-11-09:** On cfd4a4b6, `grep -n -i 'operator split' docs/MODEL.md` finds one use, in the note for developers of § "Independent-solution test": "The earlier method, an operator split, had an error proportional to the step". The restructure (`PL-BSMF`, #2054) fixed the clinician's text, which now calls it "the earlier method, which solved the equations only approximately". No chapter says what the operator split was, or that `PL-GS5X` replaced it with the exact matrix exponential on 2026-09-06, in the v0.4.x track.

**Why it matters.** The note explains why the test's limit does not shrink with the step, and the explanation rests on how the earlier method differed. "Operator split" is a numerical-methods term that the plain-writing rule names as unknown to `docs/MODEL.md`'s developer reader. Without a definition or a date, that reader cannot tell whether the method is still in the code.

**Done when.** The note for developers says in plain words what the earlier method did: it solved each exchange between two compartments on its own, in a fixed order within each step, so its error grew with the step (`PL-2HTF`, `PL-GS5X`). It also says that `PL-GS5X` replaced it with the exact step on 2026-09-06, in the v0.4.x track. Alternatively, the note drops the term and says only that the earlier method was approximate.

**Generator check.** One-off: a finding from the `docs/MODEL.md` structure-read sweep. One unexplained term outlived the method it named. No head's `misread:` states that fact.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Not present. At 817a4d88, § "Selected method (as implemented)" still said what the operator split was: each exchange solved exactly in sequence, a first-order (Lie/Godunov) split. `7ca66f0b` (#1947, `PL-TZ47`) removed that explanation and left the term in use. The deferral stays with that reason.
