---
id: PL-RMNP
title: Check every section of docs/MODEL.md against the code and data files: fix each plain fact error, note what PL-SZ6G will change, and file what needs the owner's clinical judgment
priority: P2
effort: M
status: done
classes: docs
feature: model-spec-accuracy
touches: docs/MODEL.md, docs/items/PL-CR81-projects-threads-in-the-v0-7-0-project-run.md, docs/items/PL-Y33V-docs-model-md-gives-sevoflurane-fat-and-muscle.md, docs/items/PL-LBVN-gas-man-s-released-settings-file-holds-mac-2-1.md
added: 2026-11-21
closed: 2026-11-21
pr: 2183
payoff: a clinician or contributor reading docs/MODEL.md is not told the simulator does something it does not do
verify: grep -qE '^\*\*Sections checked\.\*\*' docs/items/PL-RMNP*.md
sweep: reads every section of docs/MODEL.md against the code and data files, and files each claim the tree contradicts that it cannot correct as a plain fact
---

**Problem.** Check every section of docs/MODEL.md against the code and data files: fix each plain fact error, note what PL-SZ6G will change, and file what needs the owner's clinical judgment

**Why it matters.** `docs/MODEL.md` is the authoritative specification of the
model as implemented, and a clinician or a contributor who trusts a wrong
sentence in it can reach a wrong conclusion from a correct number. Of the 133
findings in `docs/blind-review-findings.tsv`, 42 are coded `doc-claim-wrong`:
a document that claims something the code does not do. That is the largest
category, ahead of 35 coded `code-bug` (`PL-WKKH`, the streamlining study's
record). Those findings were each made on the diff of one item. No pass has
read the whole document against the tree.

The project owner approved this sweep on 2026-11-21 02:00Z, in the Projects
thread "Check the model spec against the code" ("Do all 3 actually").

**How.** Each section of `docs/MODEL.md` is read against the code, the data
files under `src/anesthesia_sim/data/` and the tests it names. Every checkable
claim gets one of four verdicts:

1. **Holds.** The code does what the sentence says.
2. **Plain fact error.** The sentence states a value, name, behaviour or test
   that the tree contradicts, and the code is right. It is corrected in place,
   with no value, equation or citation of the model changed.
3. **`PL-SZ6G` will change it.** The claim is about the simulation step, how
   time is held or when a control change takes effect. `PL-SZ6G` (the build of
   one exact step per whole second) is in flight and rewrites those, so the
   claim is listed here and left as it is.
4. **Needs the owner.** The document and the code disagree and which is right
   is a clinical or modelling judgment, or the code is wrong on a path the
   safety-critical standard covers. It is filed as its own item with the
   question recorded.

Within-section restructuring of `docs/MODEL.md` stays held until `PL-48MX`
(the clinician's model description replaces what is left) closes, so a fix
here changes the sentence that is wrong and nothing around it.
`docs/INTERFACE.md` is a sibling thread's sweep and is not read here.

**Done when.** Every section of `docs/MODEL.md` has a row in a table of
sections checked in this brief, with its count of claims checked and what was
found. Each plain fact error is corrected on this item's branch. Each claim
that `PL-SZ6G` will change is listed. Each finding that needs the owner is an
item of its own.

**Generator check.** Work the owner asked for, and no new mechanism. The fact
each finding misreads is whether a `docs/MODEL.md` sentence about what the
model computes matches what it computes, which `PL-B6YV` (a document sentence
about what the model computes, checked against the code) already states as a
head. This item is the sweep of that fact over the whole document, so each
item it files is counted under `sweep:` and is not a new head.

**Sections checked.** Each section was read on 2026-11-21 against the code, the data files and the tests it names, by a separate pass per row. Each finding was then confirmed against the source before it was acted on, and a figure was re-run where the finding rested on one. About 1,950 claims were checked, and 62 statements were corrected, in 67 places.

| Section of `docs/MODEL.md` | Claims checked | Corrected here | Filed, or already filed | Left for `PL-SZ6G` |
| --- | --- | --- | --- | --- |
| Status, Purpose, Intended use, Model boundary, Assumptions | 64 | 2 | `PL-Z06P` | 2 notes |
| Conventions | about 110 | 2 | none | 1 finding, 12 notes |
| Symbols, Tissue groups, Compartment capacities | 52 | 1 | `PL-XXXJ` | 2 notes |
| Governing equations | 104 | 0 | `PL-HQQZ` | 1 note |
| Conservation of agent mass | 46 | 1 | `PL-TN2L` | 7 notes |
| Numerical method, to the numerical envelope | about 125 | 2 | none | 4 findings, 22 notes |
| The numerical envelope | 121 | 2 | `PL-TN2L`, `PL-076B` | 1 finding, 17 notes |
| Parameter provenance: the source hierarchy and where the project stands | 96 | 5 | `PL-XLDN` (already filed) | none |
| Parameter provenance: the reference patient and the table of values | about 150 | 8 | `PL-GW5R`, `PL-4G3N` and `PL-Z843` (already filed) | none |
| v0.2.0: isoflurane and desflurane, Delivery-limit and MAC parameters | 78 | 6 | `PL-LBVN` (already filed) | none |
| Misuse and misinterpretation hazards, Required invariants, Required tests to the independent-solution test | about 250 | 2 | `PL-8YBS` (already filed) | 2 findings, 19 notes |
| Published wash-in and elimination validation test, to desflurane's residual | 148 | 3 | none | 3 notes |
| The early wash-in curve, the sensitivity tests and the first 24 hours of elimination | about 320 | 4 | `PL-PKQC`, `PL-VF3H` | 4 notes |
| Mass-balance test to Canonical evaluation test, Release gate, How this document is held to the tree | about 95 | 13 | `PL-076B`, `PL-VF3H` | 6 notes |
| Known limitations, to intertissue diffusion | 112 | 5 | `PL-S64T` | none |
| Known limitations, from the reference adult to the end | 78 | 6 | `PL-GW5R` | none |

Two passages were not checked, because they merged into `main` while the check ran: § "How far a computed value can be from the exact one" and the other text of `#2121` (`PL-GJ1W`), and the vaporizer-design text of `#2171` (`PL-4BGX`). The papers behind the published values were not re-read. Where a data file or an extraction note restates a published value, the document agrees with it.

**What the corrections are.** Each changes one sentence or one table cell, and none changes a stored value, an equation or a citation. They fall into six kinds:

1. A sentence about what the code does that the code contradicts. Examples: the stored MAC "is not carried into the simulation", when `AgentUptakeSystem.for_agent` sets the opening dial from it; "The controller's own copy of the maximum", when the controller reads the maximum from the circuit; and a hazard row that named `tools/agent_identity_check.py` for a check that `tools/contrast_check.py` makes.
2. A count or a name that has gone stale: "two tier-3 citations" (three), "all four of this project's data files" (five), "two adopted primary sources" per agent file (four), `PatientParameters.weight_kg` (`ReferenceAdultParameters`), "the values selected for v0.1.0" over a table of every stored value.
3. A figure that its own table, test or arithmetic contradicts: 43 L of desflurane in an hour at 1 MAC (14 L), 3e11 units in the last place (5e9), a time constant lengthened by 3.32% (3.30%), "a quarter to two fifths" of a gap of which the lower figure is 19%, desflurane 0.034 to 0.042 above its curve (0.032 at 7.5 minutes), amplitudes that sum to 0.937 (0.936).
4. A range stated more widely than it holds: the open-circuit tail is "a third to a half of the mean curve" only at each cohort's lowest point, not over all of hours 8 to 13; the fourth compartment stays the largest term until 20.7 hours for desflurane and past the 24-hour limit for the others; the mass balance closes to a relative residual, not to 10⁻¹³ L.
5. A statement that a source was unread, when the same chapter records the reading: Mapleson 1963, and the four sources of Lowe and Ernst's compilation.
6. A pointer to the wrong document or roadmap item: § "Minimum displayed outputs" and § "Supported run length" are in `docs/INTERFACE.md`; `ROADMAP.md` item 31 plans primary partition coefficients, and item 30 moves the MAC.

**What `PL-SZ6G` will change.** `PL-SZ6G` (a run's time as a whole number of seconds) replaces the 0.001 to 0.1 s step range with one exact 1 s step. The claims below are true on `main` today and were left as they are. Eight findings sit inside passages that the build rewrites, and are listed here for it and not corrected.

Measured on 2026-11-21 with the test modules' own helpers, and worth knowing before the build:

- At a 1 s step, every shipped agent needs 2 squarings at its default flows and 3 at the widest flows. § "The numerical envelope" says "No supported setting needs a squaring", and `test_every_shipped_agent_steps_without_squarings_at_any_supported_setting` would fail. The reason the document gives for keeping the mass-balance tolerance fixed at one part in 10⁹ rests on that sentence.
- At a 1 s step the hardest corner needs 22 squarings, against the 19 that the envelope's limits were chosen to stay within.
- The fastest time constant is 5.83 s. A 1 s step is about a sixth of it and closes about 16% of the gap per step, against a sixtieth and 1.7% at 0.1 s.
- The open-circuit elimination ratios depend on the step, because the test driver discards the circuit once per step: sevoflurane 0.154059, 0.154020 and 0.153988 at 0.1, 0.05 and 0.01 s. Extrapolated to 1 s, the three agents' ratios move outside the 1 × 10⁻⁴ pin. The shipped ratios and the wash-in ratios did not move with the step to six decimals.
- The inspired fraction's drift within a clamped step is 1.1 × 10⁻³ at 0.1 s and ten times that at 1 s.
- The wash-in parameter recovery's residual is its trapezoidal sum's error, 7.9e-11 at 0.1 s, and it fell fourfold when the step was halved. At 1 s it would be near 8e-9, above `WASHIN_RELATIVE_TOLERANCE = 1e-9`. This one is inferred from the scaling, not measured.

The findings left for the build:

1. § "Conventions": "Times are in seconds throughout this document". The document gives many times in minutes and hours. The sentence is true of the equations, the code and a saved run.
2. § "Numerical method": "The error message names the check that failed and the step size". The mass-balance refusal names the check and its totals, with no step size.
3. § "Numerical method": "A test checks that all supported step sizes agree to within rounding", naming `test_step_refinement_converges`. That test compares three step sizes, three of the six fractions and sevoflurane only, over 60 s.
4. § "Supported simulation step": "A displayed digit is first wrong by a whole count at a step of about $`10^{13}`$ s" and "the model raised no error for steps below about $`10^{18}`$ s". `MAXIMUM_SQUARINGS = 32` now refuses an interval from between 10⁹ and 10¹⁰ s at the default settings.
5. § "Supported simulation step": the order of the worst and second-worst manoeuvres "is checked by `test_the_ventilator_start_binds_the_per_rate_table_at_every_rate`". The second-worst is checked by `test_the_second_worst_manoeuvre_and_the_margin_above_it`.
6. § "The numerical envelope": "A test checks both counts". The test checks the two counts of 19 at 128 corners with every flow at its maximum, and neither the 2,560-corner sweep nor the two larger ones.
7. § "Independent-solution test", the note for developers: it names only `test_exact_step_matches_the_independent_solution_everywhere`. The random runs are `test_exact_step_matches_the_independent_solution_on_randomised_trajectories`, and the repeats at 0.05 and 0.025 s are `test_the_disagreement_does_not_shrink_with_the_step`.
8. § "Step-refinement test": Euler's gaps "up to 1.8e-6" (dated 2026-11-03). A run on 2026-11-21 gave 1.7e-6 in the circuit and 7.1e-7 in the three compared concentrations.

The passages that state the step, by section:

- § "Intended use" and "Model boundary": the sentence that names `test_every_run_simulates_the_shipped_reference_adult`, which steps with `MAXIMUM_SIMULATION_STEP_S`; and "every control change is one of those instants".
- § "Time": the whole subsection. It includes the heading "Simulated time is a count of steps, not a running total", the 35 nanoseconds over four hours, "Ten steps of 0.1 s", the refusal of a step of a different size, "A faster rate takes more *whole steps*", the bullet "**A different step size.**", and "A saved run stores no samples and no step size".
- § "Symbols": the rows for $`t`$ (`SimulationState.elapsed_s`) and $`\Delta t`$ (`SimulationState.simulation_step_s`).
- § "Alveolar gas": "§ "Supported simulation step" compares the simulation step with this 5.83 s."
- § "Mass-balance identity": the two residual tables and the headroom sentence (also `PL-TN2L`); "at the shortest step of 1 ms. That delivers 0.00003 L per step, and 2592 L over the 86.4 million steps"; the four-way 24-hour measurement of 2026-10-25 and its case for compensated summation, which was made at the 1 ms step; "At 8.64e7 steps"; and the test whose `WORST_CASE_TRANSFER_PER_STEP_L` is the 1 ms figure.
- § "Numerical method" and § "Supported simulation step": the limits on the step and every provenance marker on `SIMULATION_STEP_S`, `MAXIMUM_SIMULATION_STEP_S` and `MINIMUM_SIMULATION_STEP_S`; "steps of 0.1 s of simulated time, and a control change takes effect at the start of the next step"; both timing tables and every figure drawn from them; "The step stays at 0.1 s ... for three reasons"; the per-rate table of control grids and frames; the 1 ms test; "At the smallest step, the supported run length is 86 400 000 steps"; and the three constants in the note for developers.
- § "The numerical envelope": the table rows for the step and the step count; "One step of the whole model, at 0.001 s and 0.1 s"; the criterion that the 0.1 s step needs no more squarings than a shipped run over 24 hours; the table's "Squarings at 0.1 s", "Step error" and "After 24 h" columns; the errors at 0.01 s and 0.001 s; the halt times of 4.3 s, 499 s and 934 s; "864,000"; the 900 calculations with no squaring; and "58 times looser".
- § "Required invariants": "simulated time is the number of completed steps times the run's step length", and the refusal of a step outside `MINIMUM_SIMULATION_STEP_S` to `MAXIMUM_SIMULATION_STEP_S`.
- § "Step-refinement test" and § "Independent-solution test": both subsections, whose tests compare steps of 0.1, 0.05, 0.025 and 0.001 s and whose every figure is given per step. "Controls move only on a step boundary" is among them.
- § "Published wash-in and elimination validation test": "The remaining $`F_I`$ is at most $`\dot V_A \Delta t / V_C`$ ... or 1.1 × 10⁻³"; every open-circuit figure, with the 2.33 SD residual and the dead-space and candidate tables that start from it; and "changes by 4 × 10⁻⁶ published SD" across the flow range.
- § "The first 24 hours of elimination against the published mean curves": "The model runs at the shipped 0.1 s step, sampled once a minute", the open-circuit table and crossing hours, and "within 0.08% at every minute from the fifth".
- § "Parameter-recovery test", "Closed-form agreement test", "Deterministic replay test" and "Canonical evaluation test": the tests run at `STEP_S = 0.1`, change settings at step counts, and probe fractional instants such as 1234.5 s.
- § "Release gate": "the convergence and nonnegativity tests at every supported step size".
- § "How this document is held to the tree": the example marker `<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->`, which sits in a code fence, so no check will flag it when the constant changes.

**Docs sweep.** `docs/MODEL.md` is the file this item changes. Checked for statements that the corrections make stale: `docs/INTERFACE.md` (two found: the open-circuit tail's hours in § "Supported run length", and where the use disclaimer sits. Both were handed to `PL-5FMC`, the check of `docs/INTERFACE.md` against the code, which corrected them in `af8d1ffc3` on pull request `#2181`. `PL-LCP4` was filed for them here and removed again before it reached `main`), `README.md` and `docs/ARCHITECTURE.md` (neither repeats a corrected statement), `docs/references/README.md` (agrees with the corrected sentence about where full texts are kept), the `sources` notes under `src/anesthesia_sim/data/` (seven found, filed as `PL-GW5R`), and the docstrings of the tests the corrected passages name (nine found, filed as `PL-VF3H`).

**Blind review, 2026-11-21.** Two passes read the branch. Between them they named three faults, and each was real. The corrected sentence on the open-circuit tail placed sevoflurane's lowest point near hour 13, and its lowest point over the whole run is 0.36 at minute 19, so the sentence now says "after the first hour". The corrected sentence on the fat-volume case left "The other agents have an edge at or inside those factors" applying to it, which is false for fat volume, so the sentence now gives the real reason the case runs once. And `PL-S64T` said that desflurane washes out slower on screen "at every setting", which holds at the default ventilation and not at 6 L/min or more, so the item now gives the figures by setting.

