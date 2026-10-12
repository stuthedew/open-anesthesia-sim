---
id: PL-1DP1
title: fraction_from_percent and percent_from_fraction take a bare float as given, so percent_from_fraction(0.5) from a caller mypy does not read is a Percent of 50.0 and format_percent(0.5) prints 50.00% whether the 0.5 was a fraction or a 0.5% dial, where every place a concentration is held refuses a bare float since PL-4R3W; whether the two crossings require the checked form too, or keep taking a number nobody built because it carries no form to refuse it by, is undecided (found building PL-SWD1, which refuses the other form and every other checked quantity there)
priority: P1
effort: S
status: done
classes: safety, defect
feature: parse-dont-validate
touches: src/anesthesia_sim/core/concentration.py, src/anesthesia_sim/app/formatting.py, docs/MODEL.md, tests/unit/test_concentration.py, tests/unit/test_formatting.py
added: 2026-10-11
closed: 2026-10-12
pr: 1446
payoff: a concentration crossing between fraction and percent is either proven to be the form it claims or refused, so a 0.5% setting can never be shown as 50%
verify: grep -q 'def test_fraction_from_percent_refuses_a_bare_float' tests/unit/test_concentration.py
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

**Done when.** The two conversions refuse a bare float with a `TypeError`
naming the constructor to use, with a test per direction in
`tests/unit/test_concentration.py`; every caller under `src/` passes a checked
value (the count below found all 13 already do); and the module docstring and
both function docstrings say the bare float is refused rather than taken as
given.

**Counted 2026-10-12, in the first batched design round, against
`origin/main` at 919ad967** - the count the recommendation above asked for.
Thirteen call sites under `src/` (the 14 above counted the two docstring
mentions in `concentration.py` itself), and none hands a bare float as typed:
`controller.py`, `governing_equations.py` and `circuit.py` convert a
`delivered_concentration_percent: Percent`; `chart_frame.py`'s three convert
from `fractions: Mapping[RecordedQuantity, tuple[Fraction, ...]]`;
`formatting.py`'s two take `partial_pressure_fraction: Fraction`;
`dashboard_frame.py` converts `axis_top_percent: Percent`;
`control_timeline.py` wraps `Percent(value)`; `wash_in.py`'s floor wraps
`Percent(CONCENTRATION_DISPLAY_RESOLUTION_PERCENT)`; `simulation_view.py`
converts `max_delivered_concentration_percent: Percent`. `mypy --strict` runs
over `src/` in `make check`, so a bare float at any call site it reads is
refused before the code runs. The runtime gap is a caller it does not read - a
test, a REPL, a value built dynamically - and refusing it costs two `require_`
calls, two tests and the docstrings; no caller changes.

**The recommendation stands: refuse it.** It goes to the owner on the same
screen as the rest of this batch rather than being decided here, for the two
reasons the brief gives: it reopens `PL-4R3W`'s deliberate choice (kind
unrecorded, so on ordinary evidence, and `PL-SWD1` is that evidence), and it
is a `safety`-classed concentration crossing, which the safety-critical
standard reaches. The repository's own rules point one way:
`.claude/rules/core-domain.md` § "A quantity with a check of its own is a
type, checked once" has every signature past the check take the type, and
`CLAUDE.md` prefers an obvious failure to a plausible wrong number where
correctness cannot be established, which a number of unknown form is. The one
argument for keeping it, from `concentration.py`'s module docstring - "a
number nobody built carries no form to refuse it by" - is also the reason it
cannot be converted safely. The count that would have changed this, a call
site handing a bare float at runtime, came back zero. Joined this batch at the
owner's "Add it" on the coordinator's card, 2026-10-12 12:31Z.

**Answered** (project owner, 2026-10-12, ratified, over keeping a bare float
as `PL-4R3W` chose and the module docstring records): refuse it. "Agree with
recs", in this thread at 12:51Z. `fraction_from_percent` requires a `Percent`
and `percent_from_fraction` a `Fraction`, each refusing anything else with a
`TypeError` naming the constructor to use; the module docstring's sentence
that a bare `float` is taken as given goes with it, and the count above says
no caller changes.
