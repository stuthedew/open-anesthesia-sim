---
id: PL-1DP1
title: fraction_from_percent and percent_from_fraction take a bare float as given, so percent_from_fraction(0.5) from a caller mypy does not read is a Percent of 50.0 and format_percent(0.5) prints 50.00% whether the 0.5 was a fraction or a 0.5% dial, where every place a concentration is held refuses a bare float since PL-4R3W; whether the two crossings require the checked form too, or keep taking a number nobody built because it carries no form to refuse it by, is undecided (found building PL-SWD1, which refuses the other form and every other checked quantity there)
priority: P1
effort: S
status: needs-decision
classes: safety, defect
feature: parse-dont-validate
touches: src/anesthesia_sim/core/concentration.py, tests/unit/test_concentration.py
added: 2026-10-11
payoff: a concentration crossing between fraction and percent is either proven to be the form it claims or refused, so a 0.5% setting can never be shown as 50%
---

**Problem.** fraction_from_percent and percent_from_fraction take a bare float as given, so percent_from_fraction(0.5) from a caller mypy does not read is a Percent of 50.0 and format_percent(0.5) prints 50.00% whether the 0.5 was a fraction or a 0.5% dial, where every place a concentration is held refuses a bare float since PL-4R3W; whether the two crossings require the checked form too, or keep taking a number nobody built because it carries no form to refuse it by, is undecided (found building PL-SWD1, which refuses the other form and every other checked quantity there)

**Reproduced 2026-10-11** on `main` at `16a20a4f`: `percent_from_fraction(0.5)`
returns a `Percent` of `50.0`, `fraction_from_percent(50.0)` returns `0.5`, and
`format_percent(0.5)` prints `50.00%`.

**Why it matters.** These two functions are the only crossings between the
model's fractions and the displayed percents: a factor-of-100 conversion on a
concentration, which `CLAUDE.md` names safety-critical. Since `PL-4R3W` every
place a concentration is *held* refuses a bare float, so the crossings are where
a number of unknown form still enters, and a 0.5 that was a 0.5% dial setting
comes out as 50%.

**Decision needed.** Should the two conversions refuse a bare float - require a
`Fraction` and a `Percent` respectively - or keep taking one, as their docstrings
and the module docstring say they do? Admitting it was `PL-4R3W`'s deliberate
choice (kind unrecorded), so this reopens it on ordinary evidence: `PL-SWD1`
found the other form crossing silently.

**Recommended: refuse it.** A bare float carries no form, so these two functions
cannot tell which conversion it needs, and an obvious error is what the safety
standard prefers to a plausible wrong number. The count that would change this:
how many of the 14 call sites under `src/` hand a bare float at runtime
(`chart_frame`'s `run.fractions` and `wash_in`'s floor are the candidates). If
none does, refusing costs a docstring; if some do, each wraps its value where
it is built, which is where its form is known.

**Done when.** Either the two conversions refuse a bare float with a `TypeError`
naming the constructor to use, with a test per direction, and every caller
passes a checked value; or the decision to keep taking one is recorded in the
module docstring with its reason.
