---
id: PL-LZ54
title: After whole-second stepping lands, correct each passage of docs/INTERFACE.md and docs/ARCHITECTURE.md that PL-5FMC found wrong and left for that build, wherever the build did not rewrite it
priority: P2
effort: M
status: done
classes: defect, docs
feature: run-computed-one-way
touches: docs/INTERFACE.md, docs/ARCHITECTURE.md
blocked-by: PL-Z6C8
deferred-from: v0.7.0 - a new problem: the passages describe the 0.1 s step and the chart as they were before work done after the freeze, the whole-second stepping build (#2180, d4e8200c) among it, and PL-5FMC (#2181) listed them
added: 2026-11-21
closed: 2026-11-22
payoff: A contributor reading the interface specification about the step, the chart and branching reads what the code now does, not what the 0.1 s step did.
verify: grep -qF 'The caption and the trace are computed separately' docs/INTERFACE.md
---

**Problem.** After whole-second stepping lands, correct each passage of docs/INTERFACE.md and docs/ARCHITECTURE.md that PL-5FMC found wrong and left for that build, wherever the build did not rewrite it

**Checked 2026-11-21**, at `2452b9b4e`. `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code) found about 125 passages that state something about the 0.1 s step, the two calculation paths, where a branch opens, or a figure measured under them. It edited none of them, because the whole-second stepping build (`PL-SZ6G`, `PL-MH9J`, `PL-FST0`, `PL-Z6C8`) rewrites them. Ten groups of those passages are wrong against the code today. `PL-5FMC`'s brief lists them under "Wrong today, and left for the whole-second stepping build", with the correction for each, and lists all the passages under "For the whole-second stepping build". The first blind review pass on `PL-5FMC`'s pull request found that nothing in the build's own items points at those lists, so a passage that the build does not rewrite would stay wrong.

Three examples from the first list: "One calculation produces both the caption and the trace, so they cannot disagree" (the caption reads the run's newest state and the trace reads the states that the chart evaluates), "two runs' nearest instants can differ by up to one column" (beside a branch's fork they can differ by up to the hover radius), and "Simulated time is displayed to 0.1 s" (the hover readout prints 0.01 s).

**Why it matters.** `docs/INTERFACE.md` is the authoritative statement of what the interface shows and does. A contributor reads each of these sentences as true.

**Done when.** Each of the ten groups in `PL-5FMC`'s first list is either rewritten by the build or corrected here, each passage in its second list has been read against the code after the build, and this item records the result for each group.

[superseded 2026-11-21: `PL-Z6C8` closed with the build in #2180] This item waits on `PL-Z6C8`, the last item of the build.

**Checked 2026-11-21:** the build landed in pull request 2180. It rewrote `docs/INTERFACE.md` § "Halting on a marked crossing", the two sections on how a run is stored and how branches reproduce (now § "A run stores the state of every second it reaches" and § "Each second has one stored state"), § "The shared history is identical by construction, not by measurement" and the preview's developer note, and `docs/ARCHITECTURE.md`'s sections on the run record and on branching. The other passages in `PL-5FMC`'s two lists are still this item's to read against the code.

**Checked 2026-11-22**, at `d4e8200c`, after the build merged. At least two of
the ten groups are still wrong. `grep -n 'cannot disagree' docs/INTERFACE.md`
printed line 3466, the end of "One calculation produces both the caption and
the trace, so they cannot disagree" (group 5). `grep -n 'every 4 s' docs/INTERFACE.md`
printed line 5091, which gives the column spacing for a 60-minute axis without
saying it holds only on a plot 900 px wide (group 4). Group 1, the figures for
comparing two readouts, is also the subject of `PL-VM4Q` (the reversal bound
and the largest differential in those paragraphs), so whichever item is worked
first should take both. At the Gate 3 freeze (`0947408`) a run stepped every 0.1 s
(`SIMULATION_STEP_S: Final = SimulationStep(0.1)` in `app/dashboard_frame.py`),
which is the step these passages describe.

**Generator check.** The fact is the link between a document sentence and the
tree fact it restates, which `PL-BLN0` and its family state. This item is the
planned remainder of `PL-5FMC`'s sweep, left for a build that rewrote the same
passages, so it is bookkeeping and not a re-entry.

**Done 2026-11-22**, on `lz54-work` from `8738170a`. Each group of `PL-5FMC`'s
first list was read against `src/anesthesia_sim/` after the build.

1. The readouts' two decimals and comparing two readouts: already rewritten on
   this branch, and confirmed. The threshold of $`8.0\times10^{-9}`$ counts is
   twice `EXACT_STEP_ORACLE_TOLERANCE` (4e-13) in counts, and the 7.2e-12 and
   2.1e-14 figures no longer appear. One sentence was corrected: it called all
   four supported input ranges intervals in L/min, and the delivered
   concentration's is in percent.
2. § "The canonical evaluation rule": removed by the build. No passage about
   two calculation paths remains in either document.
3. § "Interface boundary": corrected. `chart_columns` sets the number of grid
   columns, and the spacing is the time base divided by one less than that
   number.
4. The hover's instant: corrected. The 4 s and 48 s spacings now say they hold
   on a plot 900 px wide, and each run's peaks and troughs are named as drawn
   points. Two runs' printed instants differ by up to one column where one run
   draws an instant the other does not, and by up to the 12 px hover radius
   beside a fork or past the end of the shorter run (`nearest_trace_point`).
5. The F_A/F_I caption: corrected. The caption reads the snapshot's stored
   state for the reached second and the trace's right-hand end reads the same
   stored state, both through `wash_in_ratio`. So they agree exactly, and not
   only to rounding as `PL-5FMC` wrote before the build.
6. § "The control-input timeline": rewritten by the build. The
   "Closed-form agreement test" sentence and the 3.7e-15 figure are gone.
7. Displayed time: rewritten by the build. Time is shown in whole seconds, and
   the hover prints `format_elapsed` of a whole second (`_hover_instant`).
8. A compartment stepped alone: rewritten by the build, and right
   (`require_compartment_step`, 1 ms to the supported run length).
9. `docs/ARCHITECTURE.md` § "What a branch is, and what it shares with its
   parent": corrected. `resumed_at` opens at any whole second the trunk has
   reached, and `fork_at` accepts one (`PL-FST0`). `ResumePoint` holds no step
   length and no step at the fork. A bookmark branch opens from the stored
   state, and a branch's shared history is a copy of the trunk's stored states,
   not a `Keyframe` in its `RunDefinition`. The `fork_points_s` docstring still
   says `fork_at` refuses other instants, which is filed as `PL-C11P`.
10. Kept propagators: obsolete. The chart reads stored states and keeps no
    propagator, and no passage describes kept propagators.

The second list was read passage by passage. Beyond the groups, these were
corrected: the halt rationale on readings carried forward step by step;
`RunDefinition.state_at`, which no longer exists, now `segment_at`; Reset's
list and its developer note, which described a run definition that stores
states; the discarded run's record; the difference-trace paragraph, which said
a trace would show a nonzero difference before a bookmark fork; three
sentences of § "What the chart draws" and its developer notes that said the
run is evaluated at drawn instants; the fixed point at zero cardiac output
(1 + 4.7e-15 for isoflurane at 6 L/min at the one-second step, from
`tests/unit/test_wash_in.py`); the readout row's step-down widths, which were
measured with the clock's old widest string `23h59m59.9s` and are now 985,
571 and 290 px (measured 2026-11-22 offscreen, 1005, 591 and 310 px with the
old string in the same font); the share bar's first second, where the circuit
holds 99.45% at 1 s and reads `99%` with every agent (measured 2026-11-22);
and `docs/ARCHITECTURE.md`'s sentence that `drawn_window` evaluates states.

Judged still right: dated measurements that name the 0.1 s step they were
taken at (the 2026-09-06 volume runs, the 2026-09-14 fixed-budget figures,
the 53 µs step and the hover table of 2026-09-14). The elimination ratios
3.47, 1.83, 5.93 and 20.11 are states at whole seconds after a change at a
whole second, and each step is exact, so the step length moves them only by
rounding. Figures the build re-measured at one second: the halt examples, the
washout crossings, the wash-in ceiling's 1.0281 and the preview's 9.7e-11.

Files checked: `docs/INTERFACE.md`, `docs/ARCHITECTURE.md`, against
`app/controller.py`, `app/chart_frame.py`, `app/chart_time_base.py`,
`app/wash_in.py`, `app/run_series.py`, `app/dashboard_frame.py`,
`app/compartment_schematic.py`, `core/simulation_step.py`,
`core/stored_states.py`, `core/run_definition.py`, `core/rounding.py` and
`core/supported_ranges.py`. Every test name both documents cite exists, and
every `Class.member` they name exists except `SimulationController.origin_s`,
which the text names as removed. The grep for passages about the retired
step: `grep -nE '0\.1 s|tenth of a second|hundredth|evaluate_anchored|canonical|keyframe|every 4 s|cannot disagree' docs/INTERFACE.md docs/ARCHITECTURE.md`.
The three `0.1 s` lines left are dated records of the old step.
