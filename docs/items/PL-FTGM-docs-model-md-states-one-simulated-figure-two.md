---
id: PL-FTGM
title: docs/MODEL.md states one simulated figure two ways: a correct 24-hour run stays 'at least 25 times inside' one part in 10^9 in Numerical method but '27 times below' (3.73e-11) in Conservation, and the one-SD shift is 9x10^-4 pp in Supported simulation step but 8.7x10^-4 pp in two other places (copy editor structure read, 2026-11-05)
priority: P3
effort: S
status: ready
classes: defect, docs
feature: model-md-structure
touches: docs/MODEL.md
deferred-from: v0.7.0 - not present at the freeze (817a4d88): introduced after it by 662ed2f3 (#1826) and 7ca66f0b (#1947)
added: 2026-11-05
payoff: the 24-hour residual's margin reads the same in every chapter, so a reader does not mistake one run for two or suspect an error
verify: ! grep -qF 'at least 25 times a correct 24-hour run' docs/MODEL.md
---

**Problem.** docs/MODEL.md states one simulated figure two ways: a correct 24-hour run stays 'at least 25 times inside' one part in 10^9 in Numerical method but '27 times below' (3.73e-11) in Conservation, and the one-SD shift is 9x10^-4 pp in Supported simulation step but 8.7x10^-4 pp in two other places (copy editor structure read, 2026-11-05)

**Checked 2026-11-09:** On cfd4a4b6, `grep -n '25 times\|27 times\|8.7×10⁻⁴' docs/MODEL.md` finds half of the finding still present. § "Numerical method" says "The tolerance is at least 25 times a correct 24-hour run's residual, which stayed below 4e-11". § "Mass-balance identity" says the residual "stays 27 times below the halt threshold at 24 h", from the table's worst residual of 3.73e-11. Both describe one simulated run. The restructure (`PL-BSMF`, #2054) fixed the other half: the one-SD fat shift, 8.7×10⁻⁴ pp, now appears once, in § "Why the readouts show two decimals", and no 9×10⁻⁴ figure remains.

**Why it matters.** A reader who meets "at least 25 times" in one chapter and "27 times" in another has to work out that 25 comes from rounding 3.73e-11 up to 4e-11. Until they do, the two look like two different runs or a mistake. The project's rule is that a fact has one home, and the other places point at it.

**Done when.** § "Numerical method" gives the margin as § "Mass-balance identity" does, 27 times below the threshold at 24 h, or points to that section instead of restating the figure. No other chapter gives the 24-hour residual's margin in a different form.

**Generator check.** One-off: a finding from the `docs/MODEL.md` structure-read sweep. One figure was restated in a summary list with different rounding. No head's `misread:` states that fact.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Not present. At 817a4d88, `docs/MODEL.md` had neither figure. The 27-times margin and its 3.73e-11 residual came with `662ed2f3` (#1826, `PL-XST1`), and the "at least 25 times" summary came with `7ca66f0b` (#1947, `PL-TZ47`). Both are later than the freeze, so the deferral stays with that reason.
