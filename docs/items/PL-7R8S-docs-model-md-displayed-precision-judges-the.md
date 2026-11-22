---
id: PL-7R8S
title: docs/MODEL.md § Displayed precision judges the cost's significant figures against one SD of the density while every other agent amount, the liquid volume beside the cost included, is judged against a seventh of an SD, so the section applies two limits to figures with the same relative uncertainty
priority: P3
effort: S
status: done
classes: defect, ux
feature: model-claims-held-by-tests
touches: docs/INTERFACE.md, tests/unit/test_formatting.py, tests/unit/test_agent_cost.py, src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/currency_code.py, pyproject.toml, uv.lock, tools/import_boundary_check.py, docs/ARCHITECTURE.md
deferred-from: v0.7.0 - a new problem: the cost display and its three-significant-figures paragraph came with 7baae320 (2026-11-02), after the freeze
added: 2026-11-04
closed: 2026-11-22
pr: 2241
payoff: a learner reads a cost as an ordinary money figure, to the cent, and the document gives a reason that agrees with the display
tests: tests/unit/test_formatting.py::test_a_cost_is_shown_to_its_currency_s_minor_unit, tests/unit/test_formatting.py::test_a_cost_too_large_to_show_to_its_minor_unit_is_refused, tests/unit/test_formatting.py::test_four_figures_keep_the_price_per_millilitre_within_a_twentieth_of_a_percent, tests/unit/test_agent_cost.py::test_each_run_is_priced_at_its_own_agent_s_price, tests/unit/test_agent_cost.py::test_the_largest_cost_shown_depends_on_its_own_currency
verify: ! grep -qF 'At four it would be 0.010 %' docs/INTERFACE.md
---

**Problem.** `docs/INTERFACE.md` § "Displayed precision" judges the cost's significant figures against one SD of the density. It judges every other agent amount, the liquid volume beside the cost included, against a seventh of an SD. So the section applies two limits to figures with the same relative uncertainty.

**Checked 2026-11-04**, by the second blind review pass on `#2024`. The paragraph that opens "A cost is shown to three significant figures" refuses four significant figures for a cost because 0.010 % is "finer than one SD" of the density. Four figures would be about 0.19 SD (0.010 % against sevoflurane's 0.053 %), coarser than a seventh of an SD and so inside the band. `PL-SP6H` judged the whole millilitre of the volume beside the cost against the seventh. Above about 1,900 mL of sevoflurane, the whole-millilitre volume is finer than one SD, so the two figures on one line are judged by different limits.

**Why it matters.** The section gives a reason that its own rule elsewhere contradicts. Nothing on screen is finer than the band. Three figures are coarser than the band requires, which the one-sided bound allows.

**Decision needed.** Should a cost keep three significant figures, or show four, the finest the band admits? The choice is the owner's because four figures would change the last digit of a cost a learner sees.

- **A. Keep three figures**, and restate the reason as a choice inside the band, as the readouts' two decimals are a choice inside theirs. The learner sees no change.
- **B. Show four figures**, the finest count the band admits, as each agent amount shows the finest count derived for it. The cost is never finer than a cent, so only a cost of USD 10 or more changes: USD 12.3 would read USD 12.34.

**Recommendation: A.** It fixes the inconsistency in the reason without changing the display, and a cost at the reader's own price is read to a few figures, not to the cent on a long case.

[superseded 2026-11-22: the owner's answer below replaced this done-when] **Done when.** The paragraph that opens "A cost is shown to three significant figures" judges the cost's count of figures against the same limit as the other agent amounts, in the form the owner chooses, and `test_the_cost_s_and_the_price_s_precisions_follow_from_the_density_and_the_cost` computes that limit.

**Generator check.** Stock of `PL-B6YV`'s fact. The paragraph dates from `PL-1P15`, before that head closed on 2026-11-02, so this is not a re-entry.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem began after Gate 3 froze at `817a4d88`, so the item stays deferred to the next gate, and its `deferred-from:` names the commit that began it. The cost display and its three-significant-figures paragraph came with `7baae320` (2026-11-02).

**Checked 2026-11-22** against `d4e8200`: still applies, and still waits on the owner's choice between keeping three significant figures (A, recommended) and showing four (B). The paragraph that opens "A cost is shown to three significant figures" in `docs/INTERFACE.md` still says "At four it would be 0.010 %, finer than" one SD of the density.

**Answered 2026-11-22.** Neither option. A cost reads as a standard money figure, in whole units and cents, such as USD 12.34 or USD 123.45 (project owner, 2026-11-22: "Just make it look like standard money readout dollars and cents."). The density's uncertainty no longer sets how a cost is shown. A cost is not a value that patient care turns on, and a reader of a price expects it to the cent. A cost is shown to its currency's own minor unit, as CLDR's currency data gives it, read through a maintained library rather than a table written here: two decimals for USD and EUR, none for JPY. Babel's `format_currency` does this by default ("currency_digits – use the currency's number of decimal digits", default True; its example formats 1099.98 JPY as "¥1,100"; Babel documentation, numbers API page, read 2026-11-22: https://babel.readthedocs.io/en/latest/api/numbers.html). Babel is not yet a dependency, so the building session chooses the library and says what it does with a three-letter code CLDR does not know. The owner also said the app will have one currency throughout, which the reader can change (2026-11-22); that setting is its own item.

**Done when.** The agent cost View shows every cost to the cent, so USD 12.34 reads USD 12.34 and USD 123.45 reads USD 123.45. `docs/INTERFACE.md`'s paragraph that opens "A cost is shown to three significant figures" is rewritten to say a cost is shown as a money figure to its currency's minor unit, and no longer judges it against the density's SD. A test shows a cost above USD 100 printed with two decimals, and one in JPY printed with none.

**Measured 2026-11-22 by the localization research thread (`PL-SRP7`).** Qt's own money formatter takes its count of decimals from the region's currency, not from the currency it is given: on PySide6 6.11.2, `QLocale("ja_JP").toCurrencyString(1099.98, "USD")` returns "USD1,100". Babel 2.18.0's `format_currency(1099.98, "USD", locale="ja_JP")` returns "$1,099.98". So the build uses Babel, or CLDR's currency digits directly, and not `QLocale.toCurrencyString`.

**Built 2026-11-22.** The cost is rounded to its currency's minor unit, halves to even, and printed with its three-letter code first: `USD 12.34`, `USD 123.45`, `JPY 1100`, `KWD 1.235`. Four choices this session made:

1. **Babel, not CLDR's table copied here.** Babel 2.18.0 is now a dependency, and `app/currency_code.py`'s `minor_unit_decimals` is the one reader of it; `tools/import_boundary_check.py` confines Babel to that module. Babel's `get_currency_precision` returns `precisions.get(currency, precisions['DEFAULT'])[0]` (read in the installed 2.18.0 source). `PL-TLW6` (units in Settings) will need CLDR's region-to-currency data too, which Babel carries, so a second library or a copied table would be undone there.
2. **A code CLDR does not list gets two decimals.** That is CLDR's own default: Unicode Technical Standard #35, Part 3, Numbers, version 49, section "Currency Fraction Digits and Rounding" ("If a particular currency does not occur in the fractions list, then it is given the defaults ... digits ... The default is 2"; read 2026-11-22 at https://www.unicode.org/reports/tr35/tr35-numbers.html). The `DEFAULT` entry in CLDR's `common/supplemental/supplementalData.xml` on `main` reads `digits="2" rounding="0"`, and every non-cash `info` entry there has `rounding="0"`, so the count of digits is the whole rule. Cash rounding (Swiss francs to 0.05) is not applied, because a cost is not paid in cash.
3. **Zero reads `USD 0.00`, and digits are not grouped in thousands.** A placeholder look choice. Grouping waits for the region setting in `PL-TLW6`, because a comma is the decimal point in many regions.
4. **The price per millilitre keeps four significant figures.** Its old reason measured it against the cost's three-figure step, which no longer exists. `docs/INTERFACE.md` now gives the plain reason: most prices per millilitre are less than one unit of the currency, and four figures move the price by at most 0.05 %.

Files checked in the doc sweep: `docs/INTERFACE.md` (§ "Agent amounts in millilitres, and the cost", its note for developers, and § "A cost at the reader's price"), `docs/VERIFICATION.md` (the two cost hazard rows, still true), `docs/MODEL.md`, `docs/PARAMETERS.md`, `README.md` (no cost precision), `docs/ARCHITECTURE.md` (the `currency_code.py` line, updated), `pyproject.toml`.

**Blind review, 2026-11-22.** Both passes found that rounding to a fixed count of decimals raised the decimal module's `InvalidOperation` for a cost of about 1e26 or more, which a mistyped bottle price can give, and that froze the agent cost View. A cost is now shown only where two neighbouring floats are at most half a minor unit apart, about USD 3.5 × 10^13. Above that the cents would be the float's rounding, so the readout gives its "too large or too small to compute" reason (`cost_is_exact_to_its_minor_unit` in `app/formatting.py`). Pass 1 also found a stale sentence in `docs/INTERFACE.md` § "A cost at the reader's price" saying the cost's decimals depend on the price, now rewritten. Pass 2 found that a negative zero printed `USD -0.00`, now `USD 0.00`.
