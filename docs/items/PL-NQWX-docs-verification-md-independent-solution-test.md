---
id: PL-NQWX
title: docs/VERIFICATION.md § 'Independent-solution test' uses 'the operator split', the earlier approximate method, and no chapter says what it was or when the exact step replaced it (copy editor structure read, 2026-11-05)
priority: P3
effort: S
status: done
classes: docs
feature: model-md-structure
touches: docs/VERIFICATION.md
deferred-from: v0.7.0 - not present at the freeze (817a4d88): 7ca66f0b (#1947) removed the operator split's explanation and left the term
added: 2026-11-05
closed: 2026-11-22
payoff: a developer reading why the independent-solution limit does not shrink with the step learns what the earlier method was and that the code no longer uses it
verify: grep -qF 'The earlier method was an operator split, which the exact step replaced in v0.4.4' docs/VERIFICATION.md
---

**Problem.** docs/VERIFICATION.md § 'Independent-solution test' uses 'the operator split', the earlier approximate method, and no chapter says what it was or when the exact step replaced it (copy editor structure read, 2026-11-05)

**Checked 2026-11-09:** On cfd4a4b6, `grep -n -i 'operator split' docs/MODEL.md` finds one use, in the note for developers of § "Independent-solution test": "The earlier method, an operator split, had an error proportional to the step". The restructure (`PL-BSMF`, #2054) fixed the clinician's text, which now calls it "the earlier method, which solved the equations only approximately". No chapter says what the operator split was, or that `PL-GS5X` replaced it with the exact matrix exponential on 2026-09-06, in the v0.4.x track.

**Why it matters.** The note explains why the test's limit does not shrink with the step, and the explanation rests on how the earlier method differed. "Operator split" is a numerical-methods term that the plain-writing rule names as unknown to `docs/MODEL.md`'s developer reader. Without a definition or a date, that reader cannot tell whether the method is still in the code.

**Done when.** The note for developers says in plain words what the earlier method did: it solved each exchange between two compartments on its own, in a fixed order within each step, so its error grew with the step (`PL-2HTF`, `PL-GS5X`). It also says that `PL-GS5X` replaced it with the exact step on 2026-09-06, in the v0.4.x track. Alternatively, the note drops the term and says only that the earlier method was approximate.

**Generator check.** One-off: a finding from the `docs/MODEL.md` structure-read sweep. One unexplained term outlived the method it named. No head's `misread:` states that fact.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Not present. At 817a4d88, § "Selected method (as implemented)" still said what the operator split was: each exchange solved exactly in sequence, a first-order (Lie/Godunov) split. `7ca66f0b` (#1947, `PL-TZ47`) removed that explanation and left the term in use. The deferral stays with that reason.

**Checked 2026-11-22** against `d4e8200`: still applies. The note for developers in § "Independent-solution test" still says "The earlier method, an operator split, had an error proportional to the step", and no chapter of `docs/MODEL.md` or `docs/INTERFACE.md` says what the operator split was or when the exact step replaced it.

**Built 2026-11-22**, on a branch that carries `PL-48MX` (the clinician's `docs/MODEL.md`) and the sorting of the other three documents by reader. `grep -n -i 'operator split\|earlier method\|approximate method' docs/MODEL.md docs/VERIFICATION.md docs/INTERFACE.md docs/PARAMETERS.md` found "operator split" once, in the bullet of `docs/VERIFICATION.md` § "Independent-solution test" that explains why the limit is not a multiple of the step. "The earlier method" appears twelve times in that section, first in the paragraph on the $`4\times10^{-13}`$ limit, and no document said what it was or when it went.

The history was checked against the record before it was written. `git show 817a4d88:docs/MODEL.md` describes the method: five exchanges, each solved exactly while the other flows were held constant, composed in sequence into a first-order (Lie/Godunov) split whose error was proportional to the step. The merge of #376 (`d8deea50`, `PL-GS5X`) is in tag `v0.4.4`, dated 2026-09-06, and not in `v0.4.3`. `ROADMAP.md` says the same: "The exact step shipped in v0.4.4".

What changed: a new paragraph after the first use of "the earlier method" says that it was an operator split, that the exact step replaced it in v0.4.4, released on 2026-09-06, and what it did in plain words: it solved the model's exchanges one at a time in a fixed order, each exactly, while it held every other flow still, so the step as a whole had an error proportional to its length. It points to § "Selected method (as implemented)" for the exact step. The bullet that used the term now says only "The earlier method had an error proportional to the step". The term stays in the new paragraph because the tests call the method "the operator split" (for example `tests/reference/test_coupled_dynamics.py`), and the developer who reads this document knows the term. The paragraph does not list the five exchanges, because nothing in the section depends on which they were.

**Documents checked.** `docs/VERIFICATION.md` § "Independent-solution test", § "Selected method (as implemented)" and § "Supported simulation step"; `docs/MODEL.md` § "How the equations are solved" (no mention of the earlier method); `docs/INTERFACE.md` and `docs/PARAMETERS.md` (no mention).
