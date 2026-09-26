---
id: PL-8YBS
title: docs/MODEL.md's hazard row for two traces drawn on top of each other says fat's whole first hour spans under 4 px on the chart, which holds only at a 1 MAC dial: at the interface's maximum dial it spans 6.1-11.0 px
status: untriaged
touches: docs/MODEL.md
added: 2026-09-26
---

**Problem.** docs/MODEL.md's hazard row for two traces drawn on top of each other says fat's whole first hour spans under 4 px on the chart, which holds only at a 1 MAC dial: at the interface's maximum dial it spans 6.1-11.0 px

The row is in `docs/MODEL.md` § "Reasonably foreseeable misuse, and the hazards
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

**Done when.** The row states the dial its figure was measured at.

**Generator check.** A one-off: one clause lost its condition when a paragraph's
figure was summarised into a table row. `PL-CBDX`'s read of `#959` found no
second instance.
