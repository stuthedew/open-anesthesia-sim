---
id: PL-19W8
title: Hold docs/MODEL.md § "Known limitations" numeric paragraphs to named tests, write the tests § "Displayed precision" declares it owes, and count the claims found wrong (the first pass, which decides whether the rest run)
priority: P1
effort: M
status: ready
classes: docs, science
feature: model-claims-held-by-tests
touches: docs/MODEL.md, tools/doc_check.py, tests/reference, docs/items
deferred-from: v0.7.0 - filed 2026-11-02 as an annotation pass of PL-B6YV's rule; docs/MODEL.md traceability work that the schematic does not wait on
added: 2026-11-02
payoff: the numbers in Known limitations and Displayed precision are computed by a test, so a wrong one fails the build, and the count of wrong ones decides whether the other sections are worth the same work
verify: grep -q 'heading="Known limitations"' tools/doc_check.py
---

**Problem.** `docs/MODEL.md` § "Known limitations" states figures about what
the model computes, and 13 of its 41 numeric paragraphs carry no test,
marker, source or date (counted 2026-11-02 with
`_numeric_paragraph_members`). § "Displayed precision" now conforms, but
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
  1.2 percentage points). These paragraphs pass the check on a marker that
  ties a different figure, so they also declare the test they owe.

**Wrong claims found so far: three, in "Displayed precision".** Measured
2026-11-02 at 1 MAC with the default flows and a 0.1 s step, by both blind
review passes on `#1927` and rerun by `PL-B6YV`'s session on the project
interpreter. The page gave sevoflurane's fat first nonzero reading as 780 s
and isoflurane's as 1474 s, where the model gives 781.4 s and 1477.2 s.
Desflurane's fat was 236 s in one paragraph and 237 s in another, and the
model gives 236.9 s. The page said the alveoli read below 0.1 L for the
whole hour, but desflurane's hold 0.05 L by 110.5 s and 0.129 L at 3600 s.
All three were corrected in `#1927`. So the stop condition below is already
not met, and this pass's count decides only how the other passes are sized.

**Also left for this pass.** The residual paragraph ("Every residual was below
2.1 × 10⁻¹¹ L") passes only on a `not-restated:` marker. It reports a replay
on two tagged trees, so it wants the replay's date or a test. `PL-KXW1`'s own
brief gives 5.4e-11 L as the largest residual difference, which may be a
different quantity; the pass says which.

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
