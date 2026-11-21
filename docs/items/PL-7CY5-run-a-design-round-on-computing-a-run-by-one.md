---
id: PL-7CY5
title: Run a design round on computing a run by one rule: one exact step per whole second, every state stored, and time held as a whole number of seconds
priority: P1
effort: M
status: needs-decision
classes: planning
feature: standing-weight
touches: src/anesthesia_sim/core, src/anesthesia_sim/app, docs/MODEL.md, docs/INTERFACE.md
deferred-from: v0.7.0 - a design round filed on 2026-11-20, after the gate froze, on how a run is computed; it holds further work on PL-GJ1W, which v0.7.0 already defers, and changes nothing a learner sees until the owner answers
added: 2026-11-20
---

**Problem.** Run a design round on computing a run by one rule: one exact step per whole second, every state stored, and time held as a whole number of seconds

**Why it matters.** The simulator computes a run's state in three ways: by stepping at 0.1 s (`SIMULATION_STEP_S` in `src/anesthesia_sim/app/dashboard_frame.py`), by `RunDefinition.state_at`, and by the display's `evaluate` and `evaluate_anchored`. The module docstring of `src/anesthesia_sim/core/run_definition.py` says that the three agree only to rounding, so each place that compares two of them needs a tolerance. `PL-GJ1W` (each comparison of computed values picks its own tolerance) counts 13 tolerance constants and is still producing items. An instant is a `float`, as `CaseInstant` in `src/anesthesia_sim/core/supported_ranges.py` shows. `PL-WKKH` (the streamlining questions from the study of the one-shot rewrite) holds the measurements and the sources.

**The design to weigh.** The one-shot rewrite, `stuthedew/OAS-Sim-oneshot` at commit `2f37877`, has one rule. Each whole second is one exact step of the linear system, and every state is stored. Charts and readouts read the stored states. A branch copies its parent's states. Time is a whole number of seconds. No two computed values are compared, so no tolerance is chosen. In it, a 24-hour run with a control change every hour computed in 0.6 seconds and held 6.9 MB. Both versions stop a run at 24 hours.

**Answered 2026-11-20.** The owner agreed to open this round before more work goes into `PL-GJ1W` (project owner, 2026-11-20, ratified, "Agree with recs", over continuing with the pull requests planned for `PL-GJ1W` first).

**What the round does first.**

1. Count the closed items that came from two paths disagreeing, or from a floating-point instant.
2. Measure how long a 24-hour run takes at one step per second in this code.
3. Say what the roadmap's nitrous oxide, concentration and second-gas effects need from the stepping rule. They make the equations non-linear, and a closed-form solution exists only for linear ones.

**Decision needed.** Should a run be computed by one rule? The choice is the owner's, because it changes `core/` and what a learner sees. A control change would land on a whole second, where today it lands on a tenth. The round brings its counts and a recommendation with the question.

**Done when.** The owner has the round's counts and its recommendation, and has answered.

## The round, 2026-11-21

Run in a project thread at `2b17061` (`origin/main`), with `PL-WKKH`'s two follow-up commits on top.

### 1. Closed items that came from two paths disagreeing, or from a floating-point instant

Method: the closed items whose text names the stepped, canonical or display readings, the evaluation paths, a rounding unit on an instant, a float instant or step, or an instant past 86 400 s (163 matched), then a read of each title, and of the brief where the title did not settle it. A keyword search can miss an item that uses other words, so these are lower counts.

| Cause | Items | What a learner could have seen |
| --- | --- | --- |
| Two paths to one state disagree | 7: `PL-P1Z3` (stated the rule after the run became its definition), `PL-QVBR`, `PL-81Q2`, `PL-ZHTT`, `PL-XK00`, `PL-KJ9H`, `PL-D1LR` | `PL-QVBR` only: a MAC target read as reached on the trunk and not on a branch opened at the same step. `PL-81Q2` was measured and changed nothing. The other four corrected documents that size the gap between the paths. |
| A floating-point instant or step | 6: `PL-VM40`, `PL-8H2R`, `PL-9SL5`, `PL-06LS`, `PL-BPRK`, `PL-YZ17` | `PL-9SL5` (a chart's last column one rounding unit past its stop) and `PL-8H2R` (a run's last step past 86 400 s, or one step short). The other four are a hang or an overflow at steps or spacings that no control offers. |

That is 13 of 2 636 closed items. Three more closed items limit where a branch may open (`PL-B8MK`, `PL-W4XQ`, `PL-Y2SL`). They are not counted above, because rounding did not cause them. They exist because a branch can open only where the definition holds a keyframe, and a stored state at every second removes that limit.

**Of `PL-GJ1W`'s 13 tolerance constants, one rule removes two, probably a third, and part of a fourth.** It removes `LIVE_READING_GAP` (`app/bookmarks.py`) and `_GRID_UNIT_COUNT_TOLERANCE` (`app/chart_time_base.py`). It removes `STEP_COUNT_TOLERANCE` (`app/playback.py`) if the playback tick is also held as a whole number of milliseconds. It removes one of `HEIGHT_BAND`'s two reasons, the two readings of one step. Its other reason, a steady reading that rounding moves back and forth across a height, stays. The other nine stay, because they compare physical quantities or layout sizes and not two routes to one state: the agent balance (two constants), the cardiac output and flow fractions (three), the wash-in label (one), the chart's percent ticks (one) and the layout (two). **Of `PL-GJ1W`'s seven members, one rule would have prevented three:** `PL-QVBR`, `PL-81Q2` and `PL-9SL5`. `PL-XST1`, `PL-D88N`, `PL-9B1M` and `PL-N559` come from the agent balance and from fractions at their limits, which one rule does not change. So `PL-WKKH`'s statement that one rule "would remove the comparisons that `PL-GJ1W` gives tolerances to" holds for about a quarter of them.

### 2. A 24-hour run at one step per second, in this code

Measured on 2026-11-21 in the thread's container (4 cores, x86-64), with sevoflurane at the reference adult's settings and the dial changed every hour. The script reads the shipped `AgentUptakeSystem` and `matrix_exponential`.

| Route | Time for 24 h | Memory for every state |
| --- | --- | --- |
| One exact 1 s step per second, 86 400 steps, 24 propagators | 0.41 to 0.47 s over three runs | 6.2 MB as one array of nine numbers per second. 30 MB as Python tuples. |
| Today's checked step at 0.1 s, 864 000 steps | about 25 s, from 2.5 s for a tenth of the run | Nothing stored, by design |

Today's checked step costs about 29 µs, so 86 400 checked steps would take about 2.5 s. The one-shot's figures, 0.6 s and 6.9 MB, agree with these.

### 3. What nitrous oxide and the concentration and second-gas effects need from the rule

Korman and Mapleson describe the cause: with a high inspired concentration of nitrous oxide, net uptake of gas contracts the alveolar volume, which is made up by more inspired ventilation, less expired ventilation or a smaller lung volume (Korman B, Mapleson WW. Br J Anaesth 1997;78(5):618-625, doi:10.1093/bja/78.5.618, abstract read via PubMed). Their water analogue reproduces both effects by holding one of the two ventilations constant and varying the other to make up for the uptake (Mapleson WW, Korman B. Br J Anaesth 1998;81(6):837-843, doi:10.1093/bja/81.6.837, abstract read via PubMed). `PL-L2F2` reached the same conclusion for this model's fixed alveolar volume.

The step that follows is this round's own algebra, and neither paper states it. The varied ventilation equals the total uptake, and the uptake depends on the alveolar fractions, so the ventilation term multiplies one state by a function of the states. The equations are then non-linear. `matrix_exponential` solves only a linear system, so `RunDefinition.state_at` loses its exact jump to any instant. Today's design would then have to integrate forward from a keyframe on every read, and a 24-hour window would cost the whole run on every frame unless the states were stored. **So storing every state is where today's design would end up once nitrous oxide is added.** Under one rule, only the step changes: each second becomes a numerical solve instead of an exact propagation, and every reader is unchanged. Intravenous agents (`ROADMAP.md` planned-milestone item 13) use linear compartment models, so either design handles them.

### What one rule costs a learner

A control change at 1x playback would take effect at the next whole second, where today it takes effect at the next tenth. At 10x and faster nothing changes, because the interface already applies a change at the next tick, which is `multiplier x 0.1` s (`PL-NBWP`). The fastest time constant of the shipped model is 6.0 s (isoflurane, at the supported maxima of 10 L/min fresh gas, 12 L/min ventilation and 10 L/min cardiac output) and 14 to 17 s at the reference adult's own settings, computed from the eigenvalues of `build_system_matrix`.

`MAXIMUM_SIMULATION_STEP_S` (`core/simulation_step.py`) is a declared control-resolution tolerance, decided by the owner on 2026-09-06 (`PL-NBCJ`). This round measured it again with `tests/reference/test_control_resolution.py`'s own `_worst_over_agents`, at the shipped 0.1 s and at 1 s. Desflurane is the worst agent in every row.

| Manoeuvre | Largest displacement of a displayed compartment, 0.1 s delay | 1 s delay |
| --- | --- | --- |
| Case opening, dial from off to 1 MAC | 0.0067 percentage points | 0.066 |
| Unperfused load, then dial off | 0.050 | 0.50 |
| Ventilator start | 0.14 | 1.34 |

The comment beside the constant compares these with the parameter uncertainty in the first hour at 1 MAC: one standard deviation of a single measured partition coefficient moves a compartment by 0.082 (blood:gas) to 0.90 percentage points (muscle). At 1 s the case opening stays inside the smallest of these. The ventilator start, at 1.34 points for less than a second, exceeds all of them. The 1x interface would show what the 10x interface shows today.

Readouts would change once per simulated second, so once a second at 1x. Every whole second of a run could be a branch's opening.

### Established practice, read 2026-11-21

- **Simulated time as an integer.** The discrete-event simulator OMNeT++ holds simulated time as "int64_t-based, base-10 fixed-point simulation time" with one shared scale exponent, and warns that "conversion to and from double may lose precision" (OMNeT++ 6.4 API, `SimTime`, https://docs.omnetpp.org/6.4/api/group__SimTime and https://docs.omnetpp.org/6.4/api/classomnetpp_1_1SimTime, read through a fetching agent that quoted the pages).
- **A fixed step, with real time consumed in whole steps.** Fiedler asks "What if you want exact reproducibility from one run to the next given the same inputs?" and answers with "a fixed delta time value for the simulation", where "the renderer produces time and the simulation consumes it in discrete dt sized steps" (Fiedler G. "Fix Your Timestep!", 2004-06-10, https://gafferongames.com/post/fix_your_timestep/, read the same way). The same article interpolates between the last two states for smooth drawing. **That part is not recommended here**, because an interpolated value is a second route to a displayed number, which is the problem this round removes.

This round did not search for a published comparison of storing states against evaluating a closed form, so none is cited. The counts above are this repository's own evidence.

### Decision needed, and the recommendation

**Should a run be computed by one rule: time as a whole number of seconds, one exact step per second, every state stored, and every reader reading the stored states?**

**Recommendation: yes, at whole seconds.** It is the established design for a reproducible simulation, and the counts show what today's design costs: 13 closed items, three of `PL-GJ1W`'s seven members, two or three tolerance constants and three limits on where a branch opens. It is also where today's design would have to go once nitrous oxide makes the equations non-linear, so building it now saves building the closed-form reads twice. Whole seconds rather than tenths: the shipped model's fastest time constant is 6 s, the interface already works on a 1 s grid or coarser at 10x and faster, and tenths cost ten times the memory, which a second gas and several branches multiply.

What it costs:

1. **It reverses `PL-T691`** (closed 2026-09-07), which made the run its definition. That decision is dated before 2026-09-16, so its kind is unrecorded. Its stated reason was memory under a 30-day cap: 3.16 GB as samples at the 0.1 s step. The supported run is now 24 hours, and at one state per second it holds 6.2 MB.
2. **It changes the declared control resolution at 1x**, which the owner decided on 2026-09-06 (`PL-NBCJ`), from the 0.1 s figures to the 1 s figures in the table above.
3. **It is a large change to working code.** `core/run_definition.py`, `core/simulation.py`, `app/controller.py`, `app/chart_frame.py`, `app/bookmarks.py`, `app/run_series.py` and `app/playback.py` hold 9 381 lines, and 16 test files call `RunDefinition` or its evaluation paths. It would be built in several pull requests, each read by the owner. `.claude/rules/run-is-its-definition.md`, `docs/INTERFACE.md` § "The canonical evaluation rule" and `docs/MODEL.md` § "Supported simulation step" would be rewritten.
4. **`PL-GJ1W` is still needed, and becomes smaller.** Nine tolerance constants and four of its members remain, so its module stating the rounding is still built. Its weekly 24-hour run at the 1 ms step floor becomes a 24-hour run of 86 400 steps, about 2.5 s, which can run on every push, because the variable step and its floor go.

The alternatives:

- **One rule at tenths of a second.** The same design with a step of 0.1 s held as an integer count of tenths. A control change at 1x keeps today's timing. Each 24-hour run would hold 62 MB as an array and take about 4 s to compute, both ten times the figures above.
- **Keep today's design.** `PL-GJ1W`'s planned pull requests resume, and the two paths, the float instants and the limits on branching stay.

**Recommendation: one rule at whole seconds.** If the answer is yes, the build is filed as items under one feature, in this order: integer time; the stored states and one reader for the chart, readouts, marks and export; branches copying their parent's states; then removal of `RunDefinition`'s evaluation paths, the propagator store and the tolerance constants that no longer have a use. `PL-GJ1W` stays held until the first of these lands, and its module then covers what is left.

**Generator check.** Not a head, and a member of none. The round decides a design that `PL-GJ1W`, a live head, would otherwise build around.
