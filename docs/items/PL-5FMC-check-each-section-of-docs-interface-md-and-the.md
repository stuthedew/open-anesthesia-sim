---
id: PL-5FMC
title: Check each section of docs/INTERFACE.md and the other interface documents against the code, fix each plain fact error, and file each product decision the check finds
priority: P2
effort: M
status: ready
classes: docs
touches: docs/INTERFACE.md, docs/interface-provenance.md, docs/ARCHITECTURE.md, docs/items
added: 2026-11-21
payoff: each sentence of the interface specification that says what the interface shows or does is true of the code, or is an item
verify: grep -qE '^[*][*]Checked 2026-11-2[0-9][.:]' docs/items/PL-5FMC-*.md
sweep: claims in docs/INTERFACE.md and the other interface documents that the code does not do
---

**Problem.** Check each section of docs/INTERFACE.md and the other interface documents against the code, fix each plain fact error, and file each product decision the check finds

**Why it matters.** A blind review of closed work found 133 defects, and 42 of
them were a specification that claims something the code does not do, the
largest category (the one-shot study, `PL-WKKH`). `docs/INTERFACE.md` is the
authoritative statement of what the interface must show and do. A contributor
who trusts a wrong sentence there builds on behaviour that does not exist, and
a reader who trusts it can misread a displayed value.

**What to do.** The project owner asked for this sweep on 2026-11-21
("Do all 3 actually", to the coordinator's offer of an interface-spec check).

1. Read `docs/INTERFACE.md` section by section, and the interface claims of
   `docs/interface-provenance.md` and `docs/ARCHITECTURE.md`. Check each
   statement of what the interface shows or does against `src/` and the tests.
2. Confirm each reported mismatch against the source before acting on it.
3. Where the document is plainly wrong and the code is right, correct the
   sentence. Where the code is plainly wrong against the document, the fix is
   an item of its own, because a code defect needs its regression test.
4. Where the mismatch is a product decision, file an item at
   `needs-decision` with the question for the owner recorded in it.
5. Record the verdict for each section below, dated.

**What it must not do.** Restructure the document: sorting it by reader is
`PL-SY7G`, which waits on `PL-48MX`. Edit a claim that `PL-7CY5`'s build
(one exact step per whole second) will change: note those claims here
instead, because that build is changing `core/` while this sweep runs.

**Done when.** Every section of `docs/INTERFACE.md` has a dated verdict in
this item, each plain fact error is corrected, and each product decision is
an item of its own.

**Generator check.** No generator. This item is a sweep that the project
owner asked for, and it reads no workflow fact. It declares `docs/items`
only because its verdicts and the items it files are written there.

**Checked 2026-11-21.** Each of 22 sections of the three documents was read against the code at `2452b9b4e` by a checker of its own, about 3,900 sentences in all. The checkers reported 201 findings. Every correction below was confirmed against the source twice: by the checker when it reported the finding, and again before the replacement text was written. This session read each replacement before applying it and reran a sample of the commands.

- **Corrected: 157 replacements** in the three documents, each of a sentence or a short paragraph that said something the code does not do. One of them came from `PL-RMNP` (the same check of `docs/MODEL.md`), which found two wrong statements here and filed them as `PL-LCP4`. The other of its two was already corrected.
- **Filed: 14 items**, for the findings where the code is wrong or a decision is needed. Two ask the owner a question: `PL-0T2H` (what the chart marks when one dial is stepped several times) and `PL-CHX0` (whether the marks editor may cover the readouts while a run plays). `PL-PH3N` lists the docstrings and comments that the check found stale.
- **Left for the whole-second stepping build: about 125 passages**, listed under "For the whole-second stepping build" below. That build (`PL-SZ6G`, `PL-MH9J`, `PL-FST0`, `PL-Z6C8`) rewrites them, so they are not edited here, the ones that are wrong today included.

The 22 section reports, with the quoted sentence, the code read, the command run and its output for every finding, are in the project's shared folder under `interface-spec-check/`. Line numbers in this record are those of the documents at `2452b9b4e`.

**The result for each section.**

| Section | Sentences | Findings | Corrected | Items filed or annotated |
| --- | ---: | ---: | ---: | --- |
| `docs/INTERFACE.md` lines 1-241 | 150 | 7 | 6 | `PL-3DHK` (a run with both stop reasons) |
| `docs/INTERFACE.md` lines 242-491 | 150 | 7 | 4 | `PL-0T2H` (steps on one dial joined into one adjustment) |
| `docs/INTERFACE.md` lines 492-964, § "The canonical evaluation rule" | 230 | 12 | 1 | none |
| `docs/INTERFACE.md` lines 965-1372 | 230 | 12 | 11 | none |
| `docs/INTERFACE.md` lines 1373-1682 | 170 | 8 | 8 | none |
| `docs/INTERFACE.md` lines 1683-2068 | 190 | 5 | 5 | none |
| `docs/INTERFACE.md` lines 2069-2465, § "Interface boundary" | 190 | 9 | 8 | none |
| `docs/INTERFACE.md` lines 2466-2752 | 150 | 8 | 7 | `PL-4246` (the cap notice says "readouts below") and `PL-7H9X` (a pin from an earlier session) |
| `docs/INTERFACE.md` lines 2753-3041 | 210 | 8 | 6 | `PL-CHX0` (the marks editor over the readouts) |
| `docs/INTERFACE.md` lines 3042-3297 | 125 | 7 | 7 | none |
| `docs/INTERFACE.md` lines 3298-3572, § "MAC-awake as a chart reference" | 150 | 6 | 4 | `PL-7M65` (the washout test does not read one figure), and a note in `PL-LBVN` (which MAC values to store) |
| `docs/INTERFACE.md` lines 3573-3756 and 4081-4243 | 150 | 5 | 3 | a note in `PL-CJJ1` (the wash-in plot drops a crossing column) |
| `docs/INTERFACE.md` lines 3757-4080, § "Color contrast, and the standard this interface is held to" | 150 | 19 | 18 | `PL-R51H` (the price form's fields declare no colours), and a note in `PL-VZ57` (the audit's unreproduced leads) |
| `docs/INTERFACE.md` lines 4244-4630 | 170 | 11 | 5 | none |
| `docs/INTERFACE.md` lines 4631-5010 | 175 | 11 | 9 | none |
| `docs/INTERFACE.md` lines 5011-5496 | 230 | 16 | 14 | none |
| `docs/INTERFACE.md` lines 5497-5787 | 150 | 7 | 5 | `PL-57LD` (the macOS slider) and `PL-8FSN` (a new price keeps the old date) |
| `docs/INTERFACE.md` lines 5788-5932 | 75 | 6 | 4 | `PL-2TWX` (unit names spelled outside `app/display_units.py`) |
| `docs/interface-provenance.md` | 230 | 10 | 8 | none |
| `docs/ARCHITECTURE.md` lines 1-468 | 300 | 8 | 7 | none |
| `docs/ARCHITECTURE.md` lines 469-1018 | 330 | 9 | 7 | none |
| `docs/ARCHITECTURE.md` lines 1019-1449 | 200 | 10 | 9 | `PL-L1LP` (a sixth OS package), `PL-7KXN` (a refused price entry cannot be cleared) and `PL-RH43` (the macOS directory) |

A finding that is neither corrected nor filed is in one of the three lists below.

**Wrong today, and left for the whole-second stepping build.** The build should take each correction when it rewrites the passage, or check the figure again if the stepping changed it.

1. § "Why the readouts show two decimals" and the paragraphs after it (lines 4244-4630): the reversal threshold is $`8\times10^{-9}`$ counts where the text says $`1.0\times10^{-7}`$. The difference over an hour with the settings held constant is $`7.2\times10^{-12}`$ percentage points where the text says $`5.2\times10^{-12}`$. The largest difference between two compartments' gaps is $`2.1\times10^{-14}`$ where the text says $`1.1\times10^{-12}`$. One of the four supported input ranges is in percent and not in L/min. The pair comparison covers the five kinds of run that `docs/MODEL.md` § "Independent-solution test" lists, each for 600 s or 900 s.
2. § "The canonical evaluation rule" (lines 492-964): on the 45.3 s case, the two runs share 251 columns, 0 of 2 259 canonical values differ and 2 000 of the same 2 259 drawn values do. Only the controller's tests check the two results of 2026-09-14. The chart no longer draws 600 columns. A fork at a control event opens its definition at the keyframe before the fork. The roadmap's sentence about "the bound on any divergence" names `docs/MODEL.md`. The largest recorded residual is 2.13e-11 L, where the text says "below 2.1e-11 L". The readouts show a third path, the stepped state, where the text says "one of two paths".
3. § "Interface boundary" (lines 2069-2465): `chart_columns` in `app/chart_frame.py` sets the number of grid columns of the time axis, and the spacing is the time base divided by one less than that number.
4. § "The chart's hover readout: what the tooltip may show" (lines 5011-5496): the column spacing follows the plot's width, so "every 4 s" and "every 48 s" hold only on a plot 900 px wide. Beside a branch's fork, or past the end of the shorter run, two runs' printed instants can differ by up to the hover radius, and not by one column.
5. § "F_A/F_I as a displayed ratio": the caption reads the run's newest state and the trace reads the states that the chart evaluates, so they come from two evaluations and agree to within rounding.
6. § "The control-input timeline" (lines 242-491): "Closed-form agreement test" is a section of `docs/MODEL.md`, and the sentence does not say so. The 3.7e-15 figure was measured on `RunDefinition.evaluate`, which no longer draws the chart. A test holds the calculation that draws the chart now to 5e-14.
7. § "Displayed precision": the hover readout prints its instant to 0.01 s, so simulated time is not shown to 0.1 s everywhere.
8. § "Supported input ranges": a compartment advanced alone is still held to the smallest step, and to a largest step of its own, the supported run length.
9. `docs/ARCHITECTURE.md` § "What a branch is, and what it shares with its parent": a branch taken at a control event opens its definition at the keyframe before the fork (`RunDefinition.reaching_segment_at`, `SimulationController._open_at`). The measurement of what a restart does is in `docs/INTERFACE.md` § "The canonical evaluation rule" and no longer in `docs/MODEL.md`. `ResumePoint` also holds the step length that the case has used.
10. Two chart windows replace each other's kept propagators. With the F_A/F_I chart and the concentration chart on different time windows, as in the shipped Induction Workspace once a run passes 15 minutes, every frame forms every propagator again: about 113 a frame, at about 141 ms. `PL-Z6C8` holds the propagator work, and its file is held by another branch, so the finding is recorded here.

**Decided here, and not corrected.**

- § "What this list requires once the layout is the reader's" requires every window to carry the name of the run it shows. The code requires it once a second window is open. The requirement is the owner's (2026-09-16) and the break-out windows it governs are not built, so the sentence stays.
- `docs/ARCHITECTURE.md` § "Data flow": a proposed sentence about "two defaults" of the controller was not confirmed, and the text now names the one default that was.
- With the amounts in litres of vapour, the agent cost View's working line reads "11 mL of liquid x USD 0.2047 per mL of liquid" under the heading "Isoflurane delivered". The heading already says whose volume it is, so the wording stays (a placeholder, 2026-11-21).
- `ROADMAP.md` is not edited on this branch. Its planned-milestone item 34 says that the invariant tier appears in a main window "that cannot be closed while any other window is open", as the owner's ratified decision of 2026-09-16. `PL-DPY1` changed that mechanism as a placeholder, and `docs/INTERFACE.md` now requires the tier to be in view whenever any window is open. `docs/interface-provenance.md` now says what `docs/INTERFACE.md` requires. The roadmap's sentence is a record of the decision as it was taken.
- `docs/ARCHITECTURE.md` § "Where new code belongs" now says that a new View's values are computed in a module of its own under `app/` and drawn in a `qt_` module of its own, as the agent cost View and the compartment schematic are. The rule for a panel in the unconditional region is unchanged.

**Not confirmed.** Each section report lists the sentences that its checker could not confirm or refute, 102 in all. Most need a run on macOS, a rerun of a dated measurement, or a source outside the repository. The three that matter most: the macOS directory of the saved files (`PL-RH43`), the macOS slider (`PL-57LD`), and "It takes about three seconds" for the frame-cost harness, which was not run.

**For the whole-second stepping build.** These passages state something about the 0.1 s step, the two calculation paths, where a branch opens, or a figure measured under them. None is edited on this branch.

`docs/INTERFACE.md`, from the report on lines 1-241:

- lines 38-40: a control changed during play first acts at the next tick, so two playback rates give different runs.
- lines 57-67 and the provenance comment on line 68: a halt lands on the crossing step; the control grid is the playback rate times 0.1 s (0.1 s at 1x, 30 s at 300x); `SIMULATION_STEP_S = 0.1`.
- lines 73-76: a change after a halt could wait up to 30 simulated seconds.
- lines 81-93: the value at a halt lies within one simulation step of the height; the two worked examples (0.11 and 0.12 ×MAC) are for the 0.1 s step.
- lines 119-123: the height band and "about five hundred times finer".
- lines 125-128: the trunk's readings "carried forward step by step" against the readings a branch uses.
- lines 136-137 and 163-165: a step taking the run past a mark, and a mark inside the step a branch opened on (see F4).
- lines 216-225: canonical readings as one matrix exponential each, live readings about 1e-14 away, why the band exists.
- lines 227-240: live readings screening each step, `LIVE_READING_GAP`, the 2 ms and 60 µs costs, the gap measured at the 0.001 s step, and the two provenance comments.

`docs/INTERFACE.md`, from the report on lines 242-491:

- lines 272-278: a setting replaced before the next simulation step is not recorded; two moves between two steps are one change.
- lines 345-347: the run holds one stretch and one keyframe for each accepted change.
- lines 364-374: a run is stored as its settings and keyframes, nothing else is stored, and the chart is drawn from them.
- lines 376-383: the state at an instant is one calculation from the keyframe that opens its stretch.
- lines 385-395: the chart's values are computed a second way and agree with the single-instant state.
- lines 397-406: the record is defined in `core/run_definition.py`; the 2026-09-07 comparison of both ways with a stepped run.
- lines 408-414: storing the run as a record is smaller than one sample per 0.1 s step.
- lines 416-449: the cost of drawing a window, the propagators that `evaluate_anchored` keeps, and `state_at` reading none of them.
- lines 451-489: the measured frame costs with and without kept propagators.

`docs/INTERFACE.md`, from the report on lines 492-964:

- lines 494-500: a fixed 0.1 s step allows one sequence of arithmetic, and the rule restores that guarantee.
- lines 502-516: the canonical path (one calculation from a stretch's keyframe) and the display path (chained across columns).
- lines 518-526: what each path may be used for, and the refusal of display values.
- lines 528-542: how far the two paths differ, against the percent readout and the residual lines.
- lines 545-571: the two conditions on a branch (opens at a keyframe, on the case's time axis) and the subtraction they rule out.
- lines 586-596: a bookmark's instant is usually not a keyframe; 3 of the 1 201 instants; 48 of 54.
- lines 598-613: every fork opens its definition at a keyframe before the fork; the 655.3 s run.
- lines 694-704: the state at any reached instant is the definition evaluated there; 601 instants agree.
- lines 721-729: the fork is the end of the 0.1 s step that reaches the mark (45.300000000000004 s, 45.400000000000006 s).
- lines 740-746: a branch opens with the canonical readouts, not the live stepped ones.
- lines 755-760: the clock stands on a whole number of steps, and a branch forks from the canonical state inside the parent's stretch.
- lines 769-780: no divergence survives on the canonical path; the two divergences that exist.
- lines 791-810: columns on multiples of the spacing; the off-grid fork at 55.3 s; the one extra column.
- lines 812-837: drawn values at shared columns differ in the last digits for a bookmark branch.
- lines 839-872: `state_at`, `evaluate`, `evaluate_anchored`, kept propagators, `DisplayState` and the separation table.
- lines 874-914: the reaching stretch as the definition's opening; `steps_to_reach`; 12 767 of 36 001; time as step count times the step; the order of dial and reset.
- lines 916-961: the figures and the tests behind the statements above.

`docs/INTERFACE.md`, from the report on lines 965-1372:

- lines 1041-1043: pointer to `docs/MODEL.md` § "Supported simulation step" for a refused argument against a broken step.
- line 1056: the simulation step is a checked type (`SimulationStep`).
- lines 1114-1115: the simulation step is built through `require_positive_finite`.
- lines 1166-1169: before each step, the controller compares the settings key.
- lines 1249-1254: re-derive `EXACT_STEP_ORACLE_TOLERANCE` and the fastest time constant against the step.
- lines 1258-1259: a second test pins the displayed resolution and the shipped step (`SIMULATION_STEP_S`).
- lines 1266-1276: the step's minimum and maximum constants and where they are checked (also F3).

`docs/INTERFACE.md`, from the report on lines 1373-1682:

- lines 1385, 1391: at the shipped 0.1 s step the last step ends exactly on 24 hours; provenance `SIMULATION_STEP_S = 0.1`.
- lines 1532-1534: a step count past the limit is refused where `SimulationState` pairs it with its step.
- lines 1536-1538: every check on the limit reads the case's clock "as a step count or a case instant".
- lines 1541-1546: `CaseInstant` is a subclass of `float`, accepts an `int` or a `float`, stores minus zero as zero.
- lines 1559-1568: `StepCount`, and how many steps fit in 24 hours depends on the step (`maximum_step_count`, `require_supported_step_count`, the pair check in `__setattr__`).
- lines 1575-1584: the last count is decided on the product of count and step, not the quotient, because of rounding at some computed steps.
- lines 1587-1590: an instant only asked about stays a plain `float`, such as the one passed to `RunDefinition.state_at`.
- lines 1599-1603: the controller asks `require_supported_run_length` about the "last supported count" at every read and after every step.
- lines 1662-1663, 1668: the 2026-09-06 volume runs were made "at the shipped 0.1 s simulation step"; provenance `SIMULATION_STEP_S = 0.1`.

`docs/INTERFACE.md`, from the report on lines 1683-2068:

- lines 1721-1723: Reset clears the count of steps and releases the step length so that a fresh run may use a different one. (Already today a reset branch keeps its step, which the paragraph does not say.)
- lines 1723-1727: a run definition stores the state at each change of setting, from which every other state is computed.
- lines 1730-1733: a reset branch's run definition opens on the parent's stretch, with the settings recorded as a change at the fork.
- lines 1856-1857: the branch uses the trunk's step, and a fork between two steps is refused.
- lines 1904-1908: the resume point carries the step; runs at different steps are not exactly reproducible (see F2).
- lines 1913-1917: a branch is drawn on the trunk's columns, and a fork at a bookmark adds exactly one column.
- lines 1934-1938: the branch repeats the trunk's arithmetic, operation for operation, at every shared instant.
- lines 1940-1945: drawn traces of a bookmark fork can differ from the trunk's by a rounding error; a fork at a setting change agrees exactly.
- lines 1951-1962: the branch carries the trunk's keyframe and forms each propagation interval by one subtraction; a branch that restarts at the fork would not reproduce its trunk.
- lines 1964-1976: the four reproduction tests, the 251 shared columns, 5.3e-16, and 2.7e-15 over 240 columns before whole hundredths of a second.
- lines 2048-2052: a run halts on the step that crosses a bookmark, so two runs halted at one height show two instants.
- lines 2064-2067: a difference trace would show a tiny nonzero difference before a fork at a bookmark.

`docs/INTERFACE.md`, from the report on lines 2069-2465:

- lines 2131-2137: each point computed by formula from the definition; no stored series behind a trace; display values barred from other use.
- lines 2139-2148: the run advances one step every 0.1 s, more often than a chart can resolve.
- lines 2150-2154: drawn instants fall on whole hundredths of a second.
- lines 2155-2162: the point at a control change is the stored state; shown exactly.
- lines 2164-2174: one-pixel guarantee and its 6000 px exception at a hundredth of a second.
- lines 2182-2187: table spacings below 1 s and gaps computed against the 0.1 s state.
- lines 2282-2289: ticks every 0.1 s, one step per tick at real time.
- lines 2291-2305: whole steps per tick; the grid of tick boundaries per rate; pause, change, resume.
- lines 2317-2327: clock is a count of steps; lost ticks; delivered-rate measurement.
- lines 2329-2333: the window is evaluated from the definition; no stored samples.
- lines 2363-2372: spacing rounded onto hundredths and tenths (`grid_spacing_s`).
- lines 2383-2388: a keyframe at a control change, not a propagated state.
- lines 2402-2417, 2432-2437: figures computed against the state every 0.1 s; the step tolerance in percentage points.
- lines 2444-2457: 1 000 steps per tick, 53 microseconds, the 0.1 s tick, 300 steps at 300×, the 100 ms tick period.

`docs/INTERFACE.md`, from the report on lines 2466-2752:

- No sentence in the range depends on the 0.1 s step or on the three evaluation paths.
- Note, not a sentence: `test_refresh_view_formats_every_concentration_metric`, which lines 2471 and 2493-2506 cite, expects the clock to read "12.5s" from a sample at 12.5 s. If time becomes a whole number of seconds, that fixture changes, and the citation stays valid only if the test keeps its name.

`docs/INTERFACE.md`, from the report on lines 2753-3041:

- none in this range.

`docs/INTERFACE.md`, from the report on lines 3042-3297:

- lines 3203-3210: no step is resized or taken again; every drawn point is a state the run
  reached at the instant where it sits; no drawn value is estimated from its neighbours.
  Today a drawn column is the closed form evaluated at the column's instant
  (`chart_frame._run_frame`: "The window evaluates the closed form at instants where no step
  of the run produced a compartment state"), on a grid of 0.1 s or 0.01 s
  (`CHART_GRID_RESOLUTIONS_S`).
- lines 3268-3269: each drawn point is evaluated from the run's definition, under the
  constraint of § "Interface boundary".

`docs/INTERFACE.md`, from the report on lines 3298-3572:

- lines 3564-3571: the washout figures come from 0.1 s steps, each crossing is interpolated between two 0.1 s steps, and the provenance comment gives `SIMULATION_STEP_S = 0.1`. The test uses its own `STEP = SimulationStep(0.1)`, not the app's constant.
- lines 3343-3351 and 3490-3492: the printed figures 1.69%, 0.84 MAC, 2.86 min, 6.55 min, 2.29 and 7.30 min are results at 0.1 s steps. The alveolar crossing is 2.8553 min, which is 0.0003 min above the point where it would print as 2.85.

`docs/INTERFACE.md`, from the report on lines 3573-3756 and 4081-4243:

- lines 3606-3608: the plot samples the run at columns, which the chart evaluates between steps.
- lines 3657-3658: one calculation produces the caption and the trace (already false today, F4).
- lines 3692-3702: at zero cardiac output the 0.1 s stepped run settles on a fixed point about 1e-13 from the exact solution; 1 + 2.2e-14; the overshoot does not grow with run length.
- lines 3716-3717: the allowance is about 10 million times the largest overshoot seen, 9.6e-14.
- lines 3721-3724: the stretches are recomputed each frame from the columns drawn, so a stretch starts or ends only at a plotted instant.
- lines 3726-3729 and 3737: in runs stepped at 0.1 s the first value above equilibrium is at most 1.00235; provenance `SIMULATION_STEP_S = 0.1`.
- lines 3744-3748: the elimination figures 3.47, 1.83, 5.93 and 20.11 were measured on 0.1 s stepped runs.

`docs/INTERFACE.md`, from the report on lines 3757-4080:

- None in this range.

`docs/INTERFACE.md`, from the report on lines 4244-4630:

- lines 4267-4271: the 1.6×10⁻¹² and one-hour differences are rounding built up over 0.1 s steps (also F2).
- lines 4346-4349: the one-decimal times (19.3, 2.9, 8.5 and 14.8 minutes) are read from 0.1 s steps and may move in the last digit.
- lines 4350-4352: the first nonzero two-decimal readings (57, 125, 190, 237, 781 and 1477 seconds) are the first 0.1 s step rounded to a whole second.
- lines 4382-4387: the `10^{-13}` bound is measured over 100 steps of 0.1 s in the first ten seconds, against a 50-digit reference raised to the 0.1 s step.
- lines 4403-4406: `MAXIMUM_SIMULATION_STEP_S` is a tolerance in seconds, derived in `docs/MODEL.md` § "Supported simulation step".
- lines 4472-4476: every pair at every time step, 1 485 000 pairs, counts 0.1 s steps (also F9).
- lines 4482-4485: the largest difference between two gaps, measured at the 0.1 s step (also F3).
- lines 4503-4509: the threshold is twice a tolerance that was sized for runs at 0.1, 0.05 and 0.025 s steps (also F1).
- lines 4533-4534 and 4610-4621: the step-down widths (1005, 591, 310 px) and the 79 px, 9 px, 1068 px and 1060 px figures depend on the clock's widest string, `23h59m59.9s`, which `WIDEST_READOUT_VALUE` builds from `SIMULATION_STEP_S` and which carries a tenth of a second.

`docs/INTERFACE.md`, from the report on lines 4631-5010:

- lines 4633-4636: time is displayed to 0.1 s, one simulation step, and each control change is stamped at that resolution (`SIMULATION_STEP_S = 0.1`). Also F2.
- lines 4640-4643: the example `1h23m45.6s`, and tenths of a second appearing where there are some.
- lines 4657-4661: the tenths are there so that a stamp identifies the simulation step.
- lines 4951-4953: the circuit holds more than 99.5% of the agent "for about the first second". Today the share bar reads `Circuit >99%` from 0.1 s to 0.9 s and `99%` at 1 s (0.9945), with every agent. A run whose first state is at 1 s would never show `>99%` there.

`docs/INTERFACE.md`, from the report on lines 5011-5496:

- lines 5045-5048: the instant is printed to the hundredth of a second and is exact.
- lines 5073-5076: columns fall on whole hundredths, every other drawn instant falls on a simulation step, and the box rounds to `HOVER_INSTANT_RESOLUTION_S` (a tenth of the 0.1 s step). Open item `PL-3L8G` (ready) already asks that this claim name the step it depends on.
- lines 5214-5219: which columns a run is drawn at (also F2).
- lines 5225-5228: two runs' nearest instants differ by up to one column (also F3).
- lines 5246-5250: "the trace is drawn at about one sample per 4 s".
- lines 5402-5415: the measured table's instants (48.3 s, 289.9 s, 1208.1 s) are not whole seconds.

`docs/INTERFACE.md`, from the report on lines 5497-5787:

- lines 5535-5541: the preview starts from the run's state as § "The canonical evaluation rule" defines it, and matches the run "to within the computer's rounding error".
- lines 5545-5548: a release applies the value and records one change "at that moment".
- lines 5570-5572: the preview "has a run definition of its own" and "is evaluated on the same time grid as the run" (`evaluate_anchored`).

`docs/INTERFACE.md`, from the report on lines 5788-5932:

- None. No sentence in this range describes the step, the three evaluation paths or their tolerances. The instant line prints whatever `format_elapsed` prints for the snapshot's time, under either build.

`docs/ARCHITECTURE.md`, from the report on lines 1-468:

- line 98: `CaseInstant` and `StepCount` as the map describes them (a float instant, a step count times a step).
- line 99: `simulation_step.py` holds the step's supported range and `SimulationStep`.
- line 114: `run_definition.py` is "a run as its settings over time; any state in closed form".
- line 119: `run_series.py`'s `DrawnWindow` is the window one frame reads evaluated values from.
- line 138: `playback.py` turns a rate into whole simulation steps per tick.
- line 148: `chart_time_base.py` rules the chart's window (its grid resolutions are derived from the 0.1 s step).
- lines 326-334: values across the run are evaluated on request by `drawn_window`, and no samples are kept.
- lines 364-371: the run is held as settings plus one keyframe per change, and every other state is one propagation from a keyframe.
- lines 372-378: `evaluate` and `evaluate_anchored`, and the propagators kept from the last window.
- lines 380-388: `run_segments`, and the two evaluation paths of `docs/INTERFACE.md` § "The canonical evaluation rule".
- lines 390-397: `DisplayState` keeps a drawn value from becoming a keyframe or an opening state.
- lines 399-404: the run definition is the only record of the run.
- lines 406-414: the evaluated instants sit on an absolute grid, and a following window gains at most one column.
- lines 416-419: `chart_frame.py` is the layer above the anchored evaluation, with one column per pixel.
- lines 449-453: a playback rate is a step count, and a rate that does not give a whole count is refused.
- lines 464-466: the two timers and their intervals (`SIMULATION_TICK_INTERVAL_S` is set from the 0.1 s step).

`docs/ARCHITECTURE.md`, from the report on lines 469-1018:

- lines 638-640: 3 of the 1 201 instants on a 120 s run are keyframes (a 0.1 s step).
- lines 494-497, 526-527, 668-669: a branch's opening state is the trunk's run definition evaluated at the fork.
- lines 506-508, 513-519, 524-525, 667-668, 705-707, 729-732: a mark can lie inside a step, so the marked instant and the step instant differ, and the crossing rule finds the step.
- lines 481-487, 593-601: the definition opens at a keyframe on one time axis, and what that is worth in floating point.
- lines 622-628: no method restarts a definition at the fork, and a restart stops reproducing the trunk.
- lines 641-650: the definition opens before the fork because recording a keyframe at a halt would change the trunk's later results.
- lines 808-813: the runs agree before the fork by construction, through the shared keyframe, with zero residual.

`docs/ARCHITECTURE.md`, from the report on lines 1019-1449:

- lines 1374-1377: a panel asks `SimulationController.drawn_window(start_s, stop_s, columns)` for the span it draws. This is a possible change only: the signature takes times as floats, and the method evaluates between stored states.
