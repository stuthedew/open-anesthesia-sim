---
id: PL-8YBS
title: docs/MODEL.md's hazard row for two traces drawn on top of each other says fat's whole first hour spans under 4 px on the chart, which holds only at a 1 MAC dial: at the interface's maximum dial it spans 6.1-11.0 px
priority: P2
effort: S
status: ready
classes: docs
feature: compartment-trace-legibility
touches: docs/MODEL.md, docs/VERIFICATION.md
added: 2026-09-26
payoff: the authoritative specification states the fat-trace pixel figure with the dial it holds at, so no later session copies a 1 MAC measurement onward as true at every dial
verify: grep -qF "fat's whole first hour spans under 4 px at a 1 MAC dial and under 12 px at the agent's vaporizer maximum" docs/VERIFICATION.md
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

**Checked 2026-11-22** against `d4e8200`: still applies, but the sentence it would fix has been reworded. In the hazard row "reading one compartment's concentration as another's where two traces are drawn on top of each other", `docs/MODEL.md` now says "the fat trace moves less than 4 px over its whole first hour", still with no dial. #1944 (`20e39f39`) wrote that wording. The verbatim clause that the done-when and `verify:` require was written against the old wording, so the fix should condition the sentence as it now reads, and `verify:` should be rewritten to match. The figures were measured at the old 0.1 s step, and #2180 now steps a run in whole seconds; re-measure them before quoting them. The row moves with `PL-6PPZ` (claimed elsewhere) to a new verification document.
