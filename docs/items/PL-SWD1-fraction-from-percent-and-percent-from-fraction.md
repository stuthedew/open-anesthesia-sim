---
id: PL-SWD1
title: fraction_from_percent and percent_from_fraction take the other type silently - percent_from_fraction(Percent(0.5)) is a Percent of 50.0 and fraction_from_percent(Fraction(0.5)) a Fraction of 0.005 - because the arithmetic runs first and the constructor's swapped-type check sees a plain float; refuse a Percent where a Fraction is handed in and the reverse, as the constructors do, before converting (found reviewing PL-LLMN)
priority: P1
effort: S
status: ready
classes: safety, defect
feature: parse-dont-validate
touches: src/anesthesia_sim/core/concentration.py, tests/unit/test_concentration.py
added: 2026-10-05
payoff: a concentration handed to the wrong conversion is refused, never returned as a plausible value a hundred times too large or too small under the type meant to prove it was checked
verify: grep -q 'def test_neither_conversion_takes_the_form_it_converts_to' tests/unit/test_concentration.py
---

**Problem.** fraction_from_percent and percent_from_fraction take the other type silently - percent_from_fraction(Percent(0.5)) is a Percent of 50.0 and fraction_from_percent(Fraction(0.5)) a Fraction of 0.005 - because the arithmetic runs first and the constructor's swapped-type check sees a plain float; refuse a Percent where a Fraction is handed in and the reverse, as the constructors do, before converting (found reviewing PL-LLMN)

**Reproduced 2026-10-05, at triage.** On Python 3.14.7, against `main` at
`b67dace8`,
`uv run python -c "from anesthesia_sim.core.concentration import Fraction, Percent, fraction_from_percent, percent_from_fraction; p = percent_from_fraction(Percent(0.5)); f = fraction_from_percent(Fraction(0.5)); print(type(p).__name__, repr(p), type(f).__name__, repr(f))"`
printed `Percent 50.0 Fraction 0.005`: a dial of 0.5% handed to the display
direction came back a `Percent` of 50, and a fraction of 0.5 handed to the
model direction a `Fraction` of 0.005, each inside its range and so held as
the checked type. `mypy --strict` refuses both calls (run on a scratch file the
same day), so none of the conversions' callers in `src/` can make them.

**Why it matters.** The two conversions are the one place a concentration
crosses between its two forms, and `core/concentration.py` made `Fraction` and
`Percent` separate checked types so that the missing or doubled conversion - a
value a hundred times too large or too small - is refused rather than drawn.
The constructors and `require_fraction` and `require_percent` refuse it; the
conversions, which a caller reaches for exactly when it is crossing, do not.
What reaches them is a caller `mypy` does not read - a notebook, a test, a
value typed `Any` - and for that caller the doubled conversion becomes a
plausible concentration under the type that is meant to prove it was checked,
which nothing downstream re-checks: the silent wrong clinical value `CLAUDE.md`'s
safety-critical standard forbids.

**Done when.** `fraction_from_percent` refuses a `Fraction` and
`percent_from_fraction` refuses a `Percent`, each with a `TypeError` naming the
value as the form it already is, before any arithmetic runs; whether that
reuses `_fraction_where_a_percent_belongs` and its mirror or words its own
advice is the implementer's call, since theirs tells the caller to convert,
which is the wrong remedy for a value already in the form asked for. A `Percent`
and a `Fraction` of their own kind convert as today, and the two docstrings stop
naming this item as outstanding. A test in `tests/unit/test_concentration.py`
named `test_neither_conversion_takes_the_form_it_converts_to` pins both.
