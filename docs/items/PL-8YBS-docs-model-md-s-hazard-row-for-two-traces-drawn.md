---
id: PL-8YBS
title: docs/MODEL.md's hazard row for two traces drawn on top of each other says fat's whole first hour spans under 4 px on the chart, which holds only at a 1 MAC dial: at the interface's maximum dial it spans 6.1-11.0 px
priority: P2
effort: S
status: done
classes: docs
feature: chart-readout
touches: docs/MODEL.md, docs/VERIFICATION.md, tests/unit/test_chart_frame.py
added: 2026-09-26
closed: 2026-11-22
pr: 2262
payoff: the authoritative specification states the fat-trace pixel figure with the dial it holds at, so no later session copies a 1 MAC measurement onward as true at every dial
tests: tests/unit/test_chart_frame.py::test_at_opening_settings_fat_first_hour_spans_under_4_px_at_1_mac_and_12_px_at_vaporizer_maximum
verify: grep -qF 'less than 4 px over its whole first hour at a 1 MAC dial, and less than 12 px at the agent' docs/VERIFICATION.md
---

**Problem.** docs/MODEL.md's hazard row for two traces drawn on top of each other says fat's whole first hour spans under 4 px on the chart, which holds only at a 1 MAC dial: at the interface's maximum dial it spans 6.1-11.0 px

The row is in `docs/VERIFICATION.md` § "Reasonably foreseeable misuse, and the hazards
the presentation carries", the one reading "reading one compartment's
concentration as another's where two traces are drawn on top of each other".
`#959` (`PL-QYBW`) wrote its clause "on which fat's whole first hour spans under
4 px" from a measurement taken at a 1 MAC dial, and the condition did not travel
with it. § "Where more than one trace answers" states it ("At a 1 MAC dial on
the three shipped agents ... fat 1.5–3.7 px"); the row states the figure bare.

**Measured** (`PL-CBDX`, 2026-09-26, tree at `a0ac88c4`, whose `src/` is
unchanged since `#959`). Reference adult from `AgentUptakeSystem.for_agent`,
0.1 s steps, the delivered partial pressure set to the circuit's
`max_delivered_partial_pressure_fraction` from t = 0, and a pixel taken as
percent / `formatting.chart_axis_top_percent(MAC)` × `theme.CHART_HEIGHT`. Fat
at 60 min:

| Agent | Maximum dial | Fat at 60 min, max dial | Fat at 60 min, 1 MAC dial |
| --- | --- | ---: | ---: |
| Sevoflurane | 8.0% = 4.00 MAC | 7.72 px | 1.93 px |
| Isoflurane | 5.0% = 4.17 MAC | 6.11 px | 1.47 px |
| Desflurane | 18.0% = 3.00 MAC | 11.01 px | 3.67 px |

The 1 MAC column reproduces `PL-QYBW`'s 1.5–3.7 px, so the measurement is right
and only the row's statement of it is unconditioned.

**Why it matters, and why only a little.** No displayed value changes, and the
row's conclusion survives: 11 px is still inside the 12 px hover radius, so the
rule it justifies - every compartment in reach answers under its own name -
holds at every dial. What is wrong is a quantitative sentence in the
authoritative specification stated without the setting it holds at, which a
later session can copy onward as a general fact about the chart.

**Fix.** Condition the clause, for example "on which, at a 1 MAC dial, fat's
whole first hour spans under 4 px, and under 12 px at the interface's maximum
dial".

**Reproduced 2026-09-26** on `78b1a02b`: `grep -n "fat's whole first hour"
docs/MODEL.md` finds the clause once, in the hazard row, with no dial. The
1 MAC condition is stated only in § "Where more than one trace answers". `git
diff --stat a0ac88c4 HEAD -- src/` is empty, so `PL-CBDX`'s figures still hold
on this tree.

**Done when.** The row states the dial its figure was measured at. The
clause reads, verbatim: "on which fat's whole first hour spans under 4 px at a
1 MAC dial and under 12 px at the agent's vaporizer maximum". The rest of the
row is unchanged. The wording uses the specification's own term, "vaporizer
maximum" (from the hazard row about a setting above it, and the "Maximum
delivered concentration" parameter rows), rather than the Fix's "the
interface's maximum dial". It is fixed here so that the `verify:` can pin it.

**Generator check.** A one-off: one clause lost its condition when a paragraph's
figure was summarised into a table row. `PL-CBDX`'s read of `#959` found no
second instance.

**Checked 2026-11-02:** still open, and the sentence is still on the page
without its dial. Its generator check above called it a one-off. It is now a
member of `PL-B6YV`, the head for `docs/MODEL.md` sentences about what the
model computes that no test computes. Six other such sentences were filed
since 2026-09-06, five of them by one blind review on 2026-10-25. The repair
here is unchanged. If `PL-B6YV`'s rule is adopted, the corrected row should
also name a test that computes the pixel figure at the dial it states.

**Checked 2026-11-22** against `d4e8200`: still applies, but the sentence it would fix has been reworded. In the hazard row "reading one compartment's concentration as another's where two traces are drawn on top of each other", `docs/VERIFICATION.md` now says "the fat trace moves less than 4 px over its whole first hour", still with no dial. #1944 (`20e39f39`) wrote that wording. The verbatim clause that the done-when and `verify:` require was written against the old wording, so the fix should condition the sentence as it now reads, and `verify:` should be rewritten to match. The figures were measured at the old 0.1 s step, and #2180 now steps a run in whole seconds; re-measure them before quoting them. The row moves with `PL-6PPZ` (claimed elsewhere) to a new verification document.

**Done 2026-11-22.** Re-measured at the one-second step and the MAC at age 40, with the chart's whole preferred height (`theme.CHART_HEIGHT`, 360 px) as the scale, which bounds the percent axis from above. Fat at 60 min spans 1.47 px (isoflurane), 1.93 px (sevoflurane) and 3.67 px (desflurane) at a 1 MAC dial, and 6.27, 8.57 and 10.01 px at each agent's vaporizer maximum. Both stay under the figures the row now states, and under the 12 px hover radius. The row in `docs/VERIFICATION.md` now states the figure with every condition it holds at: the chart at its preferred height, and the reference adult at the opening ventilation, cardiac output and fresh gas flow. It reads "less than 4 px over its whole first hour at a 1 MAC dial, and less than 12 px at the agent's vaporizer maximum", and names `test_at_opening_settings_fat_first_hour_spans_under_4_px_at_1_mac_and_12_px_at_vaporizer_maximum`, which computes the figure for each agent at both dials, as `PL-B6YV`'s rule asks. The height condition was added because an Area can stretch the chart taller than its preferred height, and the pixel figure grows with it. A taller chart separates the traces more, so the row's conclusion holds there too. `PL-K1VH` (the reader-chosen ceiling) will change the figure at its 1.5 MAC rung, where fat at the vaporizer maximum spans 12.5-20.0 px, and must restate the row for the ceiling it holds at.

Docs checked: `docs/VERIFICATION.md` (the row, and § on the hover radius), `docs/INTERFACE.md` § "MAC multiples as a display unit" (its 1 MAC figures, 1.3-3.3 px against a 320 px percent axis, agree with these against 360 px), `docs/MODEL.md` (no pixel figure for fat).

**Blind review, 2026-11-22.** Pass 1 found that the first wording still left out the ventilation, cardiac output and fresh gas flow. With all three at their highest, fat at 60 min spans 4.4 px (sevoflurane) and 8.1 px (desflurane) at a 1 MAC dial, and 15.5-21.9 px at the vaporizer maximum. Fixed: the row states those settings and says that raising them spreads the trace. It also found that the next sentence, "the slow compartments are drawn within a pixel or two of one another", no longer followed from a figure of up to 12 px. Fixed: it now says two fat traces are drawn closer together than the hover radius at those settings.

Pass 2 found the same omission, and that the test checked only the opening settings while the row stated none. Fixed by the same wording, and the test was renamed to carry its settings.
