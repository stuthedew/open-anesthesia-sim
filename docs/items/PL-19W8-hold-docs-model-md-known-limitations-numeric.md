---
id: PL-19W8
title: Hold docs/MODEL.md § "Known limitations" numeric paragraphs to named tests, write the tests § "Displayed precision" declares it owes, and count the claims found wrong (the first pass, which decides whether the rest run)
priority: P1
effort: M
status: ready
classes: docs, science
feature: model-claims-held-by-tests
touches: docs/MODEL.md, tools/doc_check.py, tests/reference, docs/items
deferred-from: v0.7.0 - not live: checked 2026-11-07 (PL-8C8W): the figures it would hold are docs/MODEL.md prose, no displayed string carries them, and holding them to tests changes no display step; whether the two-decimal step holds against the stored SDs is PL-TDX0's question, which is on this gate's list undeferred, so no learner can see a wrong value through this item
added: 2026-11-02
payoff: the numbers in Known limitations and Displayed precision are computed by a test, so a wrong one fails the build, and the count of wrong ones decides whether the other sections are worth the same work
verify: grep -q 'heading="Known limitations"' tools/doc_check.py
---

**Problem.** `docs/MODEL.md` § "Known limitations" states figures about what
the model computes, and 13 of its 41 numeric paragraphs carry no test,
marker, source or date (counted 2026-11-02 with
`_numeric_paragraph_members`). Since `PL-TCD3`, a marker holds only the
figures it ties, and 24 of the 41 paragraphs are then held by nothing
(counted 2026-11-02). § "Displayed precision" now conforms, but
seven of its paragraphs do so with ``no test yet (`PL-19W8`)``. They owe the
tests listed below.

**Why it matters.** These two sections say what a displayed value can and
cannot support. A learner reads them to judge a number on the screen. A
figure here that the model does not produce misleads that judgment.

**The rule.** `docs/MODEL.md` § "How this document is held to the tree"
says a computed claim names the test that computes it (`PL-B6YV`, project
owner, 2026-11-02, ratified). In a section listed in `BOUND_FAMILIES` with
`_numeric_paragraph_members`, `make check` fails each paragraph that states a
number with a unit and carries none of the accepted forms. `PL-B6YV` added
"Displayed precision" as the first such section. Each pass names an existing
test where one computes the claim, writes a test where none does, and
otherwise uses ``no test yet (`PL-XXXX`)`` against an open item. A figure
that is a published value is cited by a DOI, a PubMed id, an ISBN or a
journal locator. The pass then adds its sections to `BOUND_FAMILIES` in the
same change, so the check stays green.

**The tests "Displayed precision" owes.** Each is a computed figure with no
test. The preferred form is one reference test that reads the figures from
the section and runs the model, as
`tests/reference/test_mac_awake_washout_figures.py` does.

- The displacement table under "The upper limit": each coefficient perturbed
  by one published SD, at 1 MAC with the reference adult's flows, worst over
  3600 s, and that desflurane always gives the largest.
- The one-decimal erasure figures under "The lower limit": fat at 0.032% and
  0.015% at 3600 s, desflurane's fat at `0.0%` for 19.3 minutes, and muscle at
  `0.0%` for 2.9, 8.5 and 14.8 minutes. "Why not the 0.1 percentage points"
  repeats the muscle times.
- The first nonzero two-decimal readings: muscle at 57, 125 and 190 s, and fat
  at 237, 781 and 1477 s.
- Under "What this section does not yet derive": venous blood below 0.1 L for
  the hour with every agent, the alveoli below it with sevoflurane and
  isoflurane, and desflurane's alveoli at 0.1 L from about two minutes.
- The one-SD shifts of the exhaust total (0.016 to 0.042 L at 3600 s, 0.18 to
  0.23 L at 24 h), of a compartment's amount (1.4% to 12%, and desflurane's
  venous blood at 79 s holding 0.99 mL), and of a compartment's share (at most
  1.2 percentage points). Each of these paragraphs carries a marker for a
  different figure, so it also declares the test it owes. Since `PL-TCD3`
  the check requires that declaration.

**Wrong claims found so far: four, in "Displayed precision".** The fourth
is `PL-TDX0`: the section gives brain:blood SDs as the tissue coefficients'
SDs, found by both blind review passes on `#1934`. The first three were
measured 2026-11-02 at 1 MAC with the default flows and a 0.1 s step, by both blind
review passes on `#1927` and rerun by `PL-B6YV`'s session on the project
interpreter. The page gave sevoflurane's fat first nonzero reading as 780 s
and isoflurane's as 1474 s, where the model gives 781.4 s and 1477.2 s.
Desflurane's fat was 236 s in one paragraph and 237 s in another, and the
model gives 236.9 s. The page said the alveoli read below 0.1 L for the
whole hour, but desflurane's hold 0.05 L by 110.5 s and 0.129 L at 3600 s.
All three were corrected in `#1927`. So the stop condition below is already
not met, and this pass's count decides only how the other passes are sized.

**Also left for this pass.** `PL-TCD3` dated the residual paragraph ("Every
residual was below 2.1 × 10⁻¹¹ L") to its replay on 2026-10-03, and named the
tests that pin the residual's form. The paragraph says every residual was
below 2.1 × 10⁻¹¹ L, but `PL-3PJZ` records the largest as 2.13e-11 L, which
is not below it (found by `PL-TCD3`'s first blind review pass). `PL-KXW1`'s
own brief gives 5.4e-11 L as the largest residual difference, which may be a
different quantity. The pass says which figure is right, and corrects the
sentence.

**Checked 2026-11-02, after `PL-TCD3`, for sizing the other passes.** Across
the whole document, 200 of 385 numeric paragraphs are held by nothing. Before
`PL-TCD3` the count was 87. The other 113 passed only on a marker for another
figure, or on a `not-restated:` marker. In a sample of 13 of them, every
ninth, 9 had an untied figure that is a claim: a model output, a measurement
with no date, or a published value with no locator. In the other 4, the
untied figure read as a setting, a condition or a tolerance, such as "at
100 kg". That is a judgment from each paragraph's opening, not a count a
script made.

**Done when.**

1. Every paragraph in "Known limitations" that states a number with a unit
   carries an accepted form, and the section is in `BOUND_FAMILIES`.
2. The tests above exist, each `no test yet (`PL-19W8`)` in "Displayed
   precision" is replaced by the test's name, and any figure they show wrong
   is corrected.
3. This brief records how many computed claims in the two sections were
   wrong or missing a condition. If none were, `PL-JP7P`, `PL-MCQ5`,
   `PL-5C1H` and `PL-H94Q` are dropped with that count as the reason.
   Otherwise they are set ready.

**Added 2026-11-03 by `PL-XQXK`.** Widening the units the numeric-paragraph check reads made one more § "Displayed precision" paragraph a member: one count of the MAC line is 0.02 percentage points of sevoflurane, 0.012 of isoflurane and 0.06 of desflurane. `test_the_mac_resolution_is_derived_from_the_percent_resolution` holds only the property that one MAC count is coarser than one percent count, so the paragraph declares that the three figures have no test yet and names this item.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present in part when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. It stays deferred to the next gate: its `deferred-from:` records the check that no learner can see a wrong value now (`PL-8C8W`). Most of the figures it would hold were in `docs/MODEL.md` at `817a4d88`: the one-SD displacement table, the erasure figures, the first nonzero readings and 11 of the 13 unheld Known-limitations paragraphs. Some came later: § "What this section does not yet derive" (`2330f33f`, 2026-10-27), the schematic's amount and share shifts (`1f4717f2`, 2026-11-02), and two percentages (`af627f04`, `c95177a6`).

**Checked 2026-11-10 (root-cause audit).** The numeric-paragraph check still holds one section: 34 of the 470 paragraphs in `docs/MODEL.md` that state a figure with a unit (a reviewer's count, not rerun). The audit recommends working this item before any wider binding, because its count of wrong claims is what decides whether the other sections are worth the same work. Widening the check to more sections is separate work from this item. The audit recommends deciding `PL-P3GZ` (whether to split `docs/MODEL.md` by reader) before that widening, since a split changes which paragraphs exist. The project owner agreed with both on 2026-11-10 (ratified, over widening the check now).

**Progress, 2026-11-14, first slice (`#2154`).** The figures in `docs/INTERFACE.md` § "Displayed precision" that rest on no SD now have tests, in `tests/reference/test_displayed_precision_figures.py`: the one-decimal erasure times, the fat fractions at one hour, the first nonzero two-decimal readings, the MAC step in percentage points, and the amounts below the run totals' 0.1 L step. Every printed figure matched the model, so this slice found no wrong claim. One figure sits on a rounding boundary: isoflurane's muscle first reads above `<0.01%` at the 190.5 s step, printed as 190 s, so the test allows half a second either way.

The figures that rest on an SD are `PL-TDX0`'s branch's (`#2150`, `tests/integration/test_parameter_uncertainty.py`): the displacement table and its ordering, the exhausted-total shifts, and the schematic's amount and share shifts. That branch also re-points the solver figures in "Why not significant figures" ($`2\times10^{-4}`$ and $`8\times10^{-11}`$) to this item. So what is left here is:

1. Those solver figures, once `#2150` merges.
2. § "Known limitations": 50 paragraphs state a number with a unit, and 32 carry no form that holds them (counted 2026-11-14 with `_numeric_paragraph_members` and `_holds_its_figures`). Most cite a paper by author and page with no DOI, PMID or locator. Some state computed figures with no test: the lung store's share of the fast pool, the 5.8% reference-condition gap, the 6.2% humidification dilution, the 16% overshoot at 585 mmHg, and the intertissue-diffusion fat fractions.
3. The residual sentence, and the count of wrong claims that decides `PL-JP7P`, `PL-MCQ5`, `PL-5C1H` and `PL-H94Q`.

**Progress, 2026-11-14, second slice (`#2154`).** § "Known limitations" is now in `BOUND_FAMILIES`. Of the 32 paragraphs that nothing held, 16 now cite their published source by journal locator, and four name a test in `tests/reference/test_known_limitations_figures.py`. Two new notes for developers name a test and hold four more. One gains a marker tying its 18% to desflurane's stored dial maximum, three are reworded, and four name `PL-LP96`. The test redoes the section's arithmetic: the molar-volume ratio behind the 5.8% and 5.5%, the humidification dilution, the variable-bypass overshoot at 585 mmHg, Lowe and Ernst's 4.84 L/min, the fat flows implied by the fitted time constants, the muscle time constants, the gaps to Baker and Farmery's set, and Yasuda's muscle SDs. The three rewordings: two summary bullets lost a number that the paragraph below them states in full, and one sentence says "one MAC" in words. `PL-LP96` is filed for the three sets of figures that no test computes and no source in the section gives.

**Wrong claims found in this pass: two.** The section said Baker and Farmery's sevoflurane fat coefficient is 26% above this model's on the tissue:gas scale. It is 71.7 × 0.6 = 43.0 against 34.0, which is 26.5% and rounds to 27%. The test failed on the old figure with `assert '27' == '26'`, and the figure is corrected. The residual sentence in `docs/INTERFACE.md` § "The agent-accounting panel" said every residual was below 2.1 × 10⁻¹¹ L, and `PL-3PJZ` records the largest as 2.13e-11 L in both versions of that replay. `PL-KXW1`'s 5.4e-11 L is a different replay, comparing other trees, so it does not bear on this sentence. The sentence now gives the largest residual. Every figure in the first slice matched the model.

**Blind review of the second slice, 2026-11-14.** Both passes found that the humidification paragraph cited Yasuda, Targ and Eger 1989 for the stored blood:gas coefficients, which that paper did not measure. The locator was added in this slice to hold the paragraph, so the check passed on a wrong source. The sentence now cites Yasuda for the tissue:gas ratios and De Wolf et al. 2012 for the blood:gas ratios, and it no longer says the blood:gas ratios were equilibrated at 37 °C, which no source here records. Both passes also found that the vessel-rich gaps to Baker and Farmery's set, 18% and 38%, are computed from the rounded 28% that the section prints, because it prints no vessel-rich coefficient. The test's docstring now says so: the 28% rests on its citation alone. Pass 1 found that the fat spreads (17% to 19%) and the "up to 9%" gap to Yasuda's means were held only by a citation that does not state them. Three new tests read § "Parameter provenance"'s table of Yasuda's Table 1 and compute both, and they check the table's stored column against the agent files.

**Left for the last slice:** the solver figures in "Why not significant figures", which `#2150` re-points to this item, and then the closure, which sets `PL-JP7P`, `PL-MCQ5`, `PL-5C1H` and `PL-H94Q` ready, since this pass and `PL-TDX0`'s found wrong claims.
