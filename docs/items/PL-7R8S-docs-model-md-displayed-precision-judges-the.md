---
id: PL-7R8S
title: docs/MODEL.md § Displayed precision judges the cost's significant figures against one SD of the density while every other agent amount, the liquid volume beside the cost included, is judged against a seventh of an SD, so the section applies two limits to figures with the same relative uncertainty
priority: P3
effort: S
status: ready
classes: defect, ux
feature: model-claims-held-by-tests
touches: docs/MODEL.md, tests/unit/test_formatting.py, docs/INTERFACE.md
deferred-from: v0.7.0 - a new problem: the cost display and its three-significant-figures paragraph came with 7baae320 (2026-11-02), after the freeze
added: 2026-11-04
payoff: a learner reads a cost as an ordinary money figure, to the cent, and the document gives a reason that agrees with the display
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
