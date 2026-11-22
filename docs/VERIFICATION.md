# Verification and validation of the model

This document states how the simulator is shown to solve the model's
equations correctly: how the agent's mass is conserved, the numerical method
and the simulation step it supports, the invariants and tests the code must
pass, and what a release must pass. A separate document, `docs/MODEL.md`,
specifies the model those equations describe.

Two parts of this document answer other questions. One required test, in
§ "Published wash-in and elimination validation test", compares the model's
output with measurements in volunteers. It tests whether the equations
represent patients, not whether the code solves them. § "Reasonably
foreseeable misuse, and the hazards the presentation carries" lists how a
reader could misread the display, and what prevents each misreading.

The last two sections serve the other specification documents.
§ "Notes for developers on the model description" says where each part of the
model that `docs/MODEL.md` describes is held in the code, and the rules that
code must keep. § "How this document is held to the tree" gives the rules that
keep these documents true to the code. Many paragraphs here carry a hidden
comment, such as `<!-- provenance: ... -->`, that ties a number to the stored
value it repeats or says that it repeats none. `docs/PARAMETERS.md` § "The
provenance table, and the markers over restated values" explains each kind.

## Conservation of agent mass

### External delivery

The cumulative amount of agent delivered is:

$$
M_{\mathrm{delivered}}(t) = \int_0^t \dot V_FF_D\,dt
$$

### Circuit exhaust

In the semi-closed circle system, the amount of agent sent to the exhaust by
time t is:

$$
M_{\mathrm{exhausted}}(t) = \int_0^t \dot V_FF_I\,dt
$$

A machine with its surplus gas valve shut sends no agent to the exhaust. It
needs a different model. See `docs/MODEL.md` § "Low flow and the closed circuit".

### Stored amount

The total stored amount of agent is:

$$
M_{\mathrm{stored}} = M_C+M_A+M_v+\sum_i M_i
$$

Arterial blood contributes no separate term, because it is not a compartment
and contains no independent amount of agent (see `docs/MODEL.md` § "What the model represents").

### Mass-balance identity

For an initial stored amount $`M_{\mathrm{initial}}`$:

$$
M_{\mathrm{initial}} + M_{\mathrm{delivered}} = M_{\mathrm{stored}} + M_{\mathrm{exhausted}} + \varepsilon_M
$$

where $`\varepsilon_M`$ is the numerical mass-balance residual.

The identity is a bookkeeping statement over whatever terms the model
includes. It would therefore still hold, unchanged, if
$`M_{\mathrm{exhausted}} \equiv 0`$. What would no longer hold is the
interpretation of that term as agent lost from the system.

Equivalently:

$$
\varepsilon_M = M_{\mathrm{initial}} + M_{\mathrm{delivered}} - M_{\mathrm{stored}} - M_{\mathrm{exhausted}}
$$

The implementation must report both absolute and relative residuals:

$$
\varepsilon_{\mathrm{absolute}} = |\varepsilon_M|
$$

and:

$$
\varepsilon_{\mathrm{relative}} = \frac{|\varepsilon_M|}{\max(M_{\mathrm{initial}}+M_{\mathrm{delivered}}, M_{\mathrm{scale}})}
$$

Here $`M_{\mathrm{scale}}`$ is a documented small positive reference amount
that prevents division by zero (`MINIMUM_RELATIVE_SCALE_L`, given below).

**$`M_{\mathrm{initial}}`$ is counted from the system's own parts, which are
set once.** The parts are the circuit, the alveoli, the patient and the
mass-balance check, built together for one agent. Replacing a part of a built
system raises a `SimulationConfigurationError`. Without that refusal, a replacement part could fail
in two ways:

- A part holding agent that $`M_{\mathrm{initial}}`$ did not count would halt
  the next step on this identity, which would blame the numerics for a swapped
  part.
- An empty part built for another agent would pass the identity, and no check
  would find it.

The refusal applies to the parts themselves. Agent added directly to a part's
stored amount is not refused when it is added. Nor is a tissue group or venous
pool that already holds agent when it is added to the patient. This balance
detects either case at the next step or read.

`tests/unit/test_record_writes.py` walks every class in `core/`. Each field of a
mutable record must either refuse a later write or be checked against a rule,
at the write or by this identity. The test fails on any field that does
neither. A field is exempt only when its entry says why no rule ties it to
another field, says that the field is private and written only by its record's
own methods, or names the open item that will check it.

Two bounds apply, and each one addresses a different question.

**The run-time halt thresholds.** The two tolerances are defined in `core/rounding.py`, and the minimum scale in `core/agent_simulation_validation.py`:

```text
AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L = 1e-12
AGENT_ACCOUNTING_RELATIVE_TOLERANCE = 1e-9
MINIMUM_RELATIVE_SCALE_L = 1e-15
```

The absolute bound and the minimum scale carry their unit in their names, and
the relative bound has none. A step passes if it meets either bound. The
relative error divides by the starting plus delivered amount, or the minimum
scale if larger, so it never divides by zero before agent is delivered. A step
that fails both bounds stops the run. These thresholds mark where the model
refuses to show a number, not the standard the shipped model is held to.

**The mass-balance tolerance, which a release must meet, bounds the relative
residual alone.** The reference runs in
`tests/reference/test_multi_agent.py` and
`tests/reference/test_sevo_patient.py` assert it, and they restate it as
`MASS_BALANCE_RELATIVE_GATE`:

```text
MASS_BALANCE_RELATIVE_GATE = 1e-10
```

The mass-balance tolerance is relative because the residual is rounding error
that accumulates once per step. The residual therefore scales with how much agent a run has
handled. An absolute bound would measure the delivered concentration and the
run length instead of conservation. The values below come from runs on
2026-11-21 at the one-second step, over 600 s of wash-in followed by
600 s of washout:

| Agent | Dial | Delivered | $`\varepsilon_{\mathrm{absolute}}`$ | $`\varepsilon_{\mathrm{relative}}`$ |
| --- | --- | --- | --- | --- |
| isoflurane | 4% | 1.60 L | 3.042e-13 L | 1.901e-13 |
| isoflurane | 2% | 0.80 L | 1.521e-13 L | 1.901e-13 |
| desflurane | 4% | 1.60 L | 8.152e-14 L | 5.095e-14 |
| desflurane | 2% | 0.80 L | 4.076e-14 L | 5.095e-14 |


Halving the dial setting halves the absolute residual exactly. It leaves the
relative residual unchanged to four significant figures.

The value of the mass-balance tolerance comes from the table below. The table
gives the worst relative residual at any step and for any of the three agents, computed on the same day at two sets of settings. The
first set is the reference runs' own settings. The second set is the corner of
the supported envelope: fresh gas 10 L/min, alveolar ventilation 12 L/min,
cardiac output 10 L/min, and each agent at its calibrated dial maximum. Each run
delivers agent for the first half of its length and washes it out for the
second half, as the reference runs do.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->

| Horizon | Reference settings | Worst envelope corner |
| --- | --- | --- |
| 1200 s, what the reference runs cover | 1.90e-13 | 3.90e-13 |
| 1 h | 5.60e-13 | 1.06e-12 |
| 4 h | 1.94e-12 | 2.97e-12 |
| 8 h | 3.32e-12 | 4.50e-12 |

On those measurements of 2026-11-21, the mass-balance tolerance of 1e-10 is
256 times the worst residual at the horizon that the reference runs use, and
22 times the worst at 8 h. So neither moving a dial nor
lengthening a case changes what the tolerance certifies. The tolerance is an
order of magnitude stricter than the 1e-9 halt threshold. A run that meets the
tolerance has therefore shown strictly more than that it did not stop. A real conservation defect would
raise the residual by orders of magnitude, not by factors of two.

**The delivered and exhausted totals are kept by a summation that stops
rounding error from building up.** Each total adds one transfer per step.
Ordinary computer addition rounds slightly each time. For a nearly constant
transfer it rounds the same way step after step, so the error grows with the
number of steps. The largest totals in the supported settings come from
desflurane at its 18% vaporizer maximum and 10 L/min of fresh gas. That
delivers 0.03 L per step, and 2592 L over the 86 400 steps of a 24 h run.
`test_the_running_agent_totals_stay_within_a_tenth_of_the_accounting_tolerance`
runs that day and checks both totals against their exact sums.
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The method is Kahan's compensated summation. Beside each total it keeps the
part that rounding lost on the last addition, and takes it off the next
transfer. The total then stays within about two roundings of the exact sum,
however long the run (Higham, *Accuracy and Stability of Numerical
Algorithms*, 2nd ed., SIAM, 2002, §4.3, equation 4.8).
`tests/unit/test_agent_simulation_validation.py` checks both totals against an
exact sum at the largest totals the supported settings reach. Saving and
restoring a run carry these correction terms with it (`capture_state()` and
`restore_state()`), and a reset clears them (`reset()`).

With compensated summation, the computed sum of n nonnegative terms is within
$`2u + O(nu^2)`$ of the exact sum, relative to it, where $`u = 2^{-53}`$
(Higham 2002, §4.3, equation 4.8). At the 86 400 steps of the longest run the
$`O(nu^2)`$ term is about 1e-27, so the bound does not grow with the run's
length.

The desflurane run at those settings was simulated four ways on 2026-11-21,
each for 24 h. Two
settings of the patient were used. "Default" is the reference adult's alveolar
ventilation of 4 L/min and cardiac output of 5 L/min. "No uptake" sets both to
zero, so that nearly all the delivered agent is exhausted again. Each total's
drift is its relative difference from the exact sum of the same transfers. The
drift was read every 100 steps. The residual is
$`\varepsilon_{\mathrm{relative}}`$ as the halt check computes it, and its
worst value was taken over every step.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5 -->

| Summation | Patient | Worst drift, delivered | Worst drift, exhausted | Worst residual |
| --- | --- | --- | --- | --- |
| plain | default | 7.9e-13 | 2.2e-14 | 9.1e-13, at 18.96 h |
| plain | no uptake | 7.9e-13 | 8.0e-13 | 1.9e-14 |
| compensated | default | 8.5e-17 | 1.1e-16 | 1.6e-13, at 24 h |
| compensated | no uptake | 7.9e-17 | 1.1e-16 | 1.1e-14 |
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

With plain addition, each total drifts by up to 8 parts in 10¹³ over the
longest run. With no uptake, the two totals drift alike and their errors cancel
in the residual. With compensated summation, each total stays within the last
digit of the exact sum for the whole run. The remaining residual comes
from the model's own step, not the sums.

The summation was adopted on 2026-10-25, when a run could take steps as short
as 1 ms. A 24 h run then added 86.4 million transfers to each total. With plain
addition, a correct run of that length came within 2.4% of the halt threshold
of one part in a billion, and it would have been halted for agent that it had
not lost. At the one-second step, plain addition would leave the same run a
thousand times below the threshold. The script and logs of the measurement of
2026-10-25 are kept outside the repository, in the project's `v0.7.0/pl-xst1/`
folder.
<!-- not-restated: 1 ms -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- absent: v0.7.0/pl-xst1/ -->

Clipping a negative stored amount to zero does not repair mass balance. It
must not be used to conceal an unstable update.

## Numerical method

The model advances in explicit simulation time, in steps, and holds every setting constant over
each step (piecewise-constant settings).

The implementation must:

1. derive concentrations from the current stored amounts;
2. evaluate every transfer from one consistent state;
3. make each transfer between two compartments remove from one exactly what it adds to the
   other, so that such transfers leave the total stored amount unchanged;
4. calculate fresh-gas delivery and exhaust in the same step as the compartments whose boundary
   they cross, by the same method and over the same time course;
5. update the cumulative amounts delivered and exhausted;
6. advance explicit simulation time; and
7. calculate the post-step mass-balance residual.

The method in § "Selected method (as implemented)" meets the requirements for transfers and for
fresh-gas delivery and exhaust. It advances every compartment together in one step, so no
transfer is applied before another, and nothing is held fixed while another value moves. Every
rate is computed from the same state, which meets requirement 2.

In the system matrix, each transfer between two compartments is a pair of
off-diagonal entries whose contributions to the total stored amount cancel, which meets
requirement 3. A test checks this cancellation as a property of the matrix
(`tests/unit/test_governing_equations.py`).

A step is all-or-nothing. A step writes each compartment in turn, and a check can reject a value
after earlier compartments have been written. So a step that cannot be completed must leave
every tracked value exactly as it was before the step. § "Step atomicity" explains why, and what
the run is left with.

**The model takes one length of step, and works within limits on compartment volumes,
partition coefficients, delivered and stored fractions, and the mass-balance residual.**
§ "Supported simulation step" gives the results behind the step, and
§ "The numerical envelope" gives those behind the limits.

- **The step, 1 s.** Each step is exact, so the length of the step costs no accuracy. Its
  cost is that a control change reaches the model up to one second late. For an ordinary dial
  change, that delay moves a displayed value by less than one standard deviation of any
  measured partition coefficient does. For an abrupt ventilation change, it moves the alveolar
  value by more than one standard deviation of any coefficient does.
- **Compartment volumes from 0.01 to 10 000 L, and partition coefficients from 0.001 to
  10 000.** These limits sit far outside any real patient or agent. The arithmetic has been
  checked against a high-precision calculation across the whole range.
- **Delivered and stored fractions up to 0.99.**
- **The tolerance on the mass-balance residual, one part in 10⁹.**
<!-- provenance: core/simulation_step.py SIMULATION_STEP_S = 1 -->
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_VOLUME_L = 10000 -->
<!-- provenance: core/numerical_envelope.py MINIMUM_PARTITION_COEFFICIENT = 0.001 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_PARTITION_COEFFICIENT = 10000 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_INPUT_FRACTION = 0.99 -->

Each limit is set where it is for these reasons:

- The step is one second so that a run's time is a whole number of seconds, which a computer
  holds exactly.
- The smallest volume is no lower because, at 0.001 L, the error at the hardest settings grew
  to 0.049% of the state over 24 hours.
- The fraction limit is below 1 so that rounding near the top cannot carry a fraction above 1.
- The tolerance is about 100 times a correct 24-hour run's residual, which stayed below 1e-11.
  A looser tolerance would let a real accounting error pass.
<!-- not-restated: 24 hours -->

### Step atomicity

When a step of simulated time fails, the model undoes it. The run then stops, because the same
step would fail again. The model is left at the last completed step, which is a real result at a
real simulation time. Undoing the step determines only what the screen may show while the run is
stopped: that result, which a reader can reason about. The error message names the check that
failed and the totals it failed on, so nobody has to infer the cause from the numbers.

A failed step is undone because a partly applied step would leave some compartments at the new
time and others at the old time. The model never produced that set of numbers at any instant,
yet on screen they could not be told apart from numbers it did produce. The project prefers an
obvious failure to a plausible-looking number.

The model restores the eight values that change from step to step: the circuit's inspired
fraction, the alveolar amount, the three tissue amounts, the venous amount, and the running
totals of agent delivered and exhausted. Settings and parameters keep their current values.
Restoring cardiac output, for example, would undo a change that the run had accepted. If the
circuit volume has changed, it stays at its new setting, and the model restores the circuit's
saved amount of agent rather than its saved fraction.

Before each step, the model saves the eight values listed above and the
starting amount of the mass-balance check, and it restores them if the step fails
(`AgentUptakeSystem.advance()`). A failed step raises an exception (`SimulationNumericalError`).

**A run stops when a step drives an amount out of range.** No step can drive a
fraction below zero (§ "Selected method (as implemented)"). Rounding can still carry a fraction
just above 1 from a state already at 1, which no supported setting reaches. The length of the
step does not cause this stop. A rejected setting leaves a run that can go on. A run stopped this
way cannot go on, because the same step would fail again, but the last completed step that the
screen keeps is still a real result, as the opening of this section says.

The check that stops a run on an out-of-range amount is in `AgentUptakeSystem.advance()`, which
raises `SimulationNumericalError`. Besides a fraction just above 1, it covers later model changes
whose equations are not pure transfers between compartments. A rejected setting raises
`SimulationConfigurationError` instead.

### Selected method (as implemented)

**Each step solves the whole model at once, exactly.** Every setting is held constant during a
step, so within that step the six modelled fractions follow fixed linear equations, which have
an exact solution. The same step also updates two running totals: the agent delivered to the
circuit and the agent exhausted from it, at the rates in § "External delivery" and
§ "Circuit exhaust".

**The only error this method leaves is rounding.** In a 3600 s run at 1 MAC on 2026-11-21, the
agent left unaccounted for at any step was at most 1.1 picolitres, for isoflurane, and less than
one part in a trillion of the agent handled, for every agent.
<!-- not-restated: 1.1 -->

**No step can drive a fraction negative**, whatever the parameters,
because the solution is exact and every transfer rate is zero or positive. The calculation keeps
this true after rounding.

**Keeping each fraction below 1 depends on what the model accepts as input.** Without rounding, no
fraction exceeds the larger of the delivered fraction and the largest fraction the run started
with. Rounding could still carry a fraction just above 1 from a state already at 1. No supported
setting reaches that state, because every vaporizer in the simulator keeps each fraction far
below 1, even at its maximum. The model also refuses such a state as an input: the delivered
concentration and every starting fraction are limited to 0.99 of the ambient pressure.
§ "The numerical envelope" gives the largest overshoot simulated from that limit.
<!-- provenance: core/supported_ranges.py MAXIMUM_INPUT_FRACTION = 0.99 -->

**Taking the run in steps does not change the result**, because each step is exact. A test checks
that a run taken in one-second steps agrees, to within rounding, with one exact calculation over
each stretch of unchanged settings.

The test of a stepped run against the exact solution is
`test_a_generated_run_keeps_what_must_hold_after_every_action` in
`tests/unit/test_generated_runs.py` (§ "Step-refinement test").

**A test against an independent solution checks that the result is right.** It compares all six
modeled fractions with that solution of the governing equations (§ "Independent-solution test").
The comparison of the two calculations cannot show that the result is right, because a wrong
transfer rate would give the same error in both. Nor can a check that no agent goes unaccounted for, because
every transfer between compartments adds exactly what it removes.

Within a step, the six fractions follow $`dy/dt = Ay + b`$, where $`A`$
holds the rate constants and $`b`$ the constant inputs. The two running totals are the seventh
and eighth states. Adding a ninth state whose value is always 1 folds $`b`$ into $`A`$, giving
$`dy/dt = Ay`$. The exact solution is

$$
y(t+\Delta t) = \exp(A\,\Delta t)\,y(t)
$$

The model builds $`A`$ in `core/governing_equations.py`. Each entry of $`A`$ is one term of one
balance equation in `docs/MODEL.md` § "Equations" or in this document's
§ "Conservation of agent mass". The model
computes $`\exp(A\Delta t)`$ in `core/matrix_exponential.py`, which contains no physiology. That
module's docstring gives the method's source and how its constants were derived. Neither module
needs an outside library.

The totals' rates are $`\dot M_{\mathrm{delivered}} = \dot V_FF_D`$ and
$`\dot M_{\mathrm{exhausted}} = \dot V_FF_I`$. Delivered agent has a simple formula of its own.
Exhausted agent does not, because it depends on the inspired fraction as that fraction changes.
It is $`\dot V_F\int F_I\,dt`$ along the coupled solution. The step matrix that advances the
fractions also computes it, which meets requirement 4 of § "Numerical method".

Conservation is built into the matrix, but each transfer's equal-and-opposite terms cancel only
to within rounding, because the arithmetic is done in fractions. In the 3600 s runs of 2026-11-21, the largest
amount of agent left unaccounted for was 5.1e-13 L for sevoflurane, 1.1e-12 L for isoflurane and
9.6e-13 L for desflurane. As a share of the agent handled, it was at most 3.8e-13 for every agent.

The check on agent accounting (`check_agent_accounting`) accepts an error within either of two
limits: a fixed 1 picolitre, set in `AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L`, or a share of the
agent handled. A step passes on either limit, so the fixed limit can only admit an error, never
refuse one. It is the wider limit only while less than 1 mL of agent has been handled, and the
share limit decides after that. The largest share measured above, 3.8e-13, is more than a
thousand times smaller than the share limit, so no accuracy is lost.
`test_the_accounting_tolerances_are_the_documented_halt_thresholds` holds both limits, and
`test_a_residual_inside_the_absolute_tolerance_passes_on_the_absolute_branch` holds the fixed one.

In litres, though, that error scales with the largest amount in play: about 14 L of delivered
agent over an hour at desflurane's 1 MAC dial setting. A long run therefore routinely exceeds the fixed
limit and passes on the share limit alone. In runs on 2026-11-21, the fixed limit was first
exceeded after 3457 s at the reference settings, for isoflurane at 1 MAC, and after 2193 s at
the most extreme sevoflurane settings the model accepts.

The tests on the reference runs use the share limit, `MASS_BALANCE_RELATIVE_GATE`
(§ "Mass-balance identity"). A release test on the error in litres would rest on a claim that
depends on the dial setting and stops being true after about an hour of simulated time.

Every off-diagonal entry of $`A`$ is a transfer rate, so it is nonnegative. That makes $`A`$ a
Metzler matrix and $`\exp(A\Delta t)`$ an entrywise nonnegative matrix, whatever the parameters.
Shifting the matrix before summing the exponential's series keeps that true in floating point.

The capacity guard and the rollback in § "Step atomicity" cover two cases to which the reasons
above do not apply. The first is a state at the top of the range, which a caller can pass when
resuming a run (`resume_at`) or opening a prediction (`predicted_states`). Those two routes
check only that a state lies from 0 through 1. The second is a model extension whose matrix is
not a pure transfer system.

### Supported simulation step

The model advances in steps of 1 s of simulated time, and it takes no step of any other length.
Every setting is held constant across a step. So a control change takes effect at the next whole
second, up to one second after it is made.
<!-- provenance: core/simulation_step.py SIMULATION_STEP_S = 1 -->

**The step is exact at this length.** Each step solves the model's equations exactly, so a step of
any length adds no error beyond rounding, and it keeps every fraction in range. In runs on
2026-09-06 with steps from $`10^{-3}`$ s to 3600 s across the supported settings, the results
differed from an independent solution by about $`10^{-14}`$ to $`2\times10^{-12}`$ of a fraction,
and the difference did not grow with the step.

In the 2026-09-06 runs, the difference from the independent solution was smallest for steps of
about 1 to 60 s. Rounding accumulates once per step, so a finer step is slightly worse. The
propagator had no negative entry at any of the 4374 combinations of settings and step, so no
fraction is rejected for stepping coarsely. An interval that needs more than 32 squarings of the
propagator is refused before any arithmetic (§ "The numerical envelope").

**The step is one second so that simulated time is exact too.** Simulated time is the count of
steps, and a computer holds a whole number of seconds exactly
(§ "Simulated time is a count of steps, not a running total"). A step of a tenth of a second
cannot be held exactly: three such steps add up to 0.30000000000000004 s.

**A run of the supported length takes 86 400 steps**, one for each second
(`MAXIMUM_STEP_COUNT` in `core/supported_ranges.py`). The last step ends exactly at the supported
run length.
<!-- derived: 86 400 steps from core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The step is declared in `core/simulation_step.py`, as `SIMULATION_STEP_S`.
The two methods that advance the model, `AgentUptakeSystem.advance()` and
`SimulationState.advance()`, take no argument, so no caller can ask for another step. The
project owner chose the step on 2026-11-21 (ratified, `PL-7CY5`), over a step of a tenth of a
second held as a whole count of tenths, and over keeping a step held as a decimal fraction of a
second. It replaced a step of 0.1 s, chosen on 2026-09-06 (`PL-NBCJ`), at which each figure in
the table of timing errors in § "Control timing at the one-second step" was about a tenth of its
value here.

The run's state (`SimulationState`) has no method that takes steps in a loop for a caller, because
no caller in `src/` needs one. Apart from the run loop, the loops over `advance` are test helpers
that drive the controller step by step, as the interface does.

**To get the state after a set time without stepping a run, use a prediction.** A caller cannot
take a step longer than one second. That keeps the record of control changes true, so that a
stepped run is one the interface could have produced, with each setting held for whole steps.
For the states over the next 30 s or the next hour with unchanged settings, pass the system's
`equation_settings()`, the state to start from and the two seconds to `predicted_states` in
`core/prediction.py`. It takes one-second steps, as a run does, and returns the state at every
second. `predicted_states_at` returns the state at chosen seconds only, each reached from the one
before by one calculation over the gap. A test checks that a prediction stays within rounding of a run that stepped the same
seconds (`test_each_predicted_second_matches_the_second_the_run_stepped` in
`tests/unit/test_prediction.py`). The application draws its previews this way.

#### Control timing at the one-second step

**What the step costs is control resolution.** Settings are held constant across a step, so the
step is the interval over which a change to a control is invisible to the model. A slider move is
resolved to one second. A change made and reversed between two steps never reaches the model at
all.

**The step is about a sixth of the fastest process in the model.** That process has a time
constant of 5.83 s, the shortest anywhere in the supported settings (`docs/MODEL.md` § "Time constants" gives the
settings at which it occurs). In one step, the fastest process closes about 16% of its remaining
gap. So a control change that takes effect one step late can move a fast-changing value by an
amount a reader can see, and the tables below give that amount.

The 16% per step is $`1 - e^{-1/5.83} = 0.158`$.

**Control timing has no natural step, so the step is a declared tolerance.** Because a control
change waits for the next step, it is delayed by up to one whole step. The delay grows in
proportion to the step, and the error it causes in the modelled values grows with it, with no
length at which the error suddenly drops. So no step makes control timing invisible, and the
one-second step rests on the timing errors stated below.

**The tolerance, in percentage points of one atmosphere.** The table below gives the timing
error at the one-second step, in percentage points (pp) of one atmosphere. Each figure is the worst displacement, over all three agents, when a control change
lands one step late. The figures are absolute concentrations, not counts of the readout's last
digit. How many decimals the readout shows is a display choice, and it must not affect the model
(`docs/INTERFACE.md` § "Why the readouts show two decimals", note for developers).

| Manoeuvre | Worst displacement | Agent giving the worst |
| --- | --- | --- |
| Case opening: dial off to 1 MAC, reference flows | 7.3×10⁻² pp | desflurane |
| Unperfused load, then perfusion on and dial off | 5.0×10⁻¹ pp | desflurane |
| Ventilator start at the envelope corner | 1.3 pp | desflurane |

These figures are judged against the model's own parameter uncertainty, which comes before both
the step and the display. In the first hour at 1 MAC, one standard deviation (SD) of the
blood:gas coefficient displaces a displayed compartment by up to $`9.0\times10^{-2}`$ pp, and one
SD of the muscle coefficient by up to $`9.9\times10^{-1}`$ pp. The blood:gas shift is the smallest
of the four coefficients' shifts, and the muscle shift is the largest. So the timing error of an
ordinary control action is smaller than the shift from one SD of any coefficient, and in that
sense the step is fine enough. The shift for each coefficient is in `docs/INTERFACE.md` § "Why the readouts show two decimals".

**What one second does not buy.** An abrupt manoeuvre's timing error is not kept within one SD
of any coefficient. A ventilator start that takes effect one second late shifts the alveolar
reading by up to 1.3 pp. That is more than one SD of any single coefficient moves a readout in
the first hour. The shift then fades as the two runs converge: it is 1.0 pp three seconds after
the change and 0.5 pp after eight seconds. The figure is desflurane's, with the dial at its
18% maximum, the ventilator off for five minutes and ventilation then started at 12 L/min. It
is about a fifth of desflurane's 1 MAC of 6.6%. The same manoeuvre gives 0.59 pp for sevoflurane
and 0.36 pp for isoflurane. So a reader comparing an abrupt ventilation change with a
measurement should know that its *timing* is accurate to one second and no better.
<!-- provenance: data/agents/desflurane.json mac_at_age_40_percent = 6.6 -->
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->

#### Playback, and when a control change acts

**How playback takes the steps.** The program's timer runs every 100 ms of real time. Each tick
adds the playback rate times 100 ms to the simulated time that the run is owed, and the run takes
one step for each whole second owed. At real-time playback the run takes one step on every tenth
tick, so the clock and the readouts change once a second. At 5× it takes one step on every second
tick. At 20×, 60× and 300× it takes 2, 6 and 30 steps on every tick. The step is the same at
every rate.
<!-- provenance: app/dashboard_frame.py SIMULATION_TICK_INTERVAL_MS = 100 -->

**Above 5× playback, a control change can wait longer than one step.** The table above gives the
error for one step of delay. At 1× and 5×, a control change waits only for the next whole second.
At a faster rate, the program takes all the steps of a tick at once, with nothing between them.
A setting changed during playback first acts on the next step that the program takes, so the
instants that a change can reach are one tick's steps apart. So the same slider
moves made at two playback rates are different inputs, and they produce different runs. The
table below gives the control grid and its errors at each rate:

| Playback rate | Control grid | Worst displacement per grid step | Second worst | Margin |
| --- | --- | --- | --- | --- |
| 1× | 1 s | 1.3 pp | 5.0×10⁻¹ pp | 2.70× |
| 5× | 1 s | 1.3 pp | 5.0×10⁻¹ pp | 2.70× |
| 20× | 2 s | 2.5 pp | 9.8×10⁻¹ pp | 2.56× |
| 60× | 6 s | 5.8 pp | 2.8 pp | 2.11× |
| 300× | 30 s | 1.0×10¹ pp | 1.0×10¹ pp | 1.03× |

<!-- provenance: core/simulation_step.py SIMULATION_STEP_S = 1 -->

The control grid is in simulated seconds. The worst displacement is the same quantity as
in the first table, recomputed at each rate over the same three manoeuvres and all three agents
(simulated 2026-11-21). The second worst is the next manoeuvre down at that rate. The margin is
the ratio of the two, computed before rounding.

**A test keeps the two timing tables above current.** Each time the tests run, it recomputes the
tables from the parameter files. A change to the equations, a partition coefficient, the
reference adult's volumes, the supported input ranges or the step itself therefore changes the
test's result before it can make this section wrong.

The test that recomputes the two timing tables (`tests/reference/test_control_resolution.py`)
runs each manoeuvre on time and one step late, and takes the worst difference over all six
displayed compartments. It also fixes the step at which the figures were computed, because the
table and the step are one decision. The worst manoeuvre at each rate is checked by
`test_the_ventilator_start_binds_the_per_rate_table_at_every_rate`, and the second worst and the
margin by `test_the_second_worst_manoeuvre_and_the_margin_above_it`.

**Read the worst column as an upper limit over the three manoeuvres.** At every rate, the worst is
the ventilator start with desflurane, and the second worst is the unperfused load, then perfusion
on and dial off. That order came from runs of the model and could change, so a test rechecks it
whenever the tables are recomputed. At 300×, the ventilator start leads the unperfused load by
only 3%, and both round to 1.0×10¹ pp in the table. A parameter change that swapped them would
leave the limit correct but the name of the worst manoeuvre wrong.

**At higher playback rates, the errors of the ventilator start and the unperfused load converge,
because they level off at different delays.** The ventilator start's transient is largely over
within 30 s, the delay at 300×, so its error levels off instead of growing with the delay. Scaling
its 1× figure up in proportion overstates the 300× figure about four times. The unperfused load's
transient is still under way at 30 s, so its error still grows almost in proportion to the delay.
Neither the figures nor the margin can therefore be scaled between rates. Use the values in the
table.

**An ordinary dial change is well below both the worst and the second-worst columns.** It is the
case opening, a third manoeuvre, and its error is about 19 times smaller than the worst at 1× and
5×. The ratio narrows to 17 times at 20×, 14 times at 60× and about 6 times at 300×, where the case
opening reaches 1.7 pp. Use this comparison to judge what a learner's own actions cost. To see how
far the worst figure stands above the other abrupt manoeuvres, use the second-worst column. The
tens of percentage points at 300× come from abrupt manoeuvres.

Three things follow.

- **By its own record, no control change arrives late.** Each recorded control change carries the
  run's simulated time when it was made, and the new setting acts from the step that begins
  there, at every rate. So the control record is exact to the step, and no displayed value is
  stale against it. The rate limits only which instants a reader can *choose*.
- **Pause, change, resume places a change on a chosen whole second at every rate.** No steps are
  taken while the run is paused, so a setting changed during the pause acts from the step on which
  the run resumes. Use this route to time a manoeuvre, and faster playback to watch one. No route
  places a change between two whole seconds, because a run holds no instant there.
- **At 20× and faster, controls are timed twice as finely as the screen shows.** The screen is
  redrawn every 0.2 s of real time, which is every second tick. At 1× and 5× the run takes at most
  one step between two redraws, so the screen shows every step.
<!-- provenance: app/dashboard_frame.py RENDER_INTERVAL_S = 0.2 -->

The chart draws its columns at whole seconds, because a run holds no instant between two of them
(`grid_spacing_s` in `app/chart_time_base.py`).

The simulated time that playback owes a run is held in whole milliseconds, so the sum is exact at
every rate (`OwedSimulatedTime` in `app/playback.py`). The control grid at each rate is
`PlaybackRate.control_grid_s`. At 20× and faster, applying control changes between the steps of
an update, or updating more often, would time controls more finely than the screen can show. A
recorded control change is a `ControlChange`, and the simulated time it carries is
`SimulationState.elapsed_s` when it was made.

The implementation must not depend on wall-clock elapsed time, interface frame rate, the interface
toolkit, filesystem state, display size or event-loop scheduling.

The step and the tick interval are separate constants:

```text
SIMULATION_STEP_S           = 1     # core/simulation_step.py, seconds of simulated time
SIMULATION_TICK_INTERVAL_MS = 100   # app/dashboard_frame.py, milliseconds of real time
```

Each update adds `multiplier × tick interval` to the simulated time that the run is owed, and
the run takes one step for each whole second owed. The steps in each update are computed from
the playback speed and the two constants, so a test can check a speed such as "60× real time".
Someone who changes how often the program updates, to suit a different computer, changes only
the tick interval, and the speeds on screen stay true.

#### A compartment stepped on its own

**A compartment stepped on its own takes a step from 1 ms up to the supported run length.**
In a run, the compartments are stepped only by the uptake system's step method
(`AgentUptakeSystem.advance()`), always by one second. But code can step each compartment
directly, by a step that it gives as a plain number. A finer step loses more to rounding. Each
step adds its change to the stored amount. The finer the step, the smaller that change is beside
the amount, so the same rounding is a larger share of the change. The table below records runs
of 10 000 steps on 2026-10-19, with each
compartment held at a fraction of 0.01 and stepped toward 0.02. The compartments were a tissue
group with a time constant of 480 s, the venous pool at 7.8 s and the breathing circuit at 60 s:
<!-- provenance: core/supported_ranges.py MINIMUM_COMPARTMENT_STEP_S = 0.001 -->

| Step | Largest error in what the three changed by, as a share of the change |
| --- | --- |
| 0.1 s | 2e-14 |
| 1 ms | 3e-13 |
| 1 µs | 3e-11 |
| 1e-10 s | 3e-5 |
| 1e-14 s | 4% for the pool and the circuit; the tissue did not change at all |

<!-- provenance: core/supported_ranges.py MINIMUM_COMPARTMENT_STEP_S = 0.001 -->

So each compartment's own step method rejects a step below 1 ms
(`MINIMUM_COMPARTMENT_STEP_S`). The methods are `TissueGroup.advance`,
`VenousBloodCompartment.advance` and `BreathingCircuit.advance_fresh_gas`, which
`BreathingCircuit.advance` calls. The check is `require_compartment_step` in
`core/supported_ranges.py`. The error grows with no sudden jump, so the limit is declared, not
derived, at the finest step at which the figures above were taken.
<!-- provenance: core/supported_ranges.py MINIMUM_COMPARTMENT_STEP_S = 0.001 -->

**A compartment stepped on its own has its own largest step: the supported run length.** One step
cannot cover more simulated time than the span over which the model is claimed to represent a
patient (`docs/INTERFACE.md` § "Supported run length"). Without that limit, a breathing circuit stepped by about
1e308 s would compute the number of time constants elapsed (the admitted gas divided by the
circuit volume) as `inf`. The circuit's step method (`BreathingCircuit.advance_fresh_gas`) would
then return an exhaust of `inf` during wash-in. When the dial was at or below the circuit's
fraction, it would return `nan`, from zero times `inf`. At the limit, a step covers at most about
1.4 million circuit time constants, about 300 decades inside the range of a `float`. The tissue
groups and the venous pool give a finite result at any step, because the function that steps them
(`exponential_approach`) saturates at equilibrium. They still take the same limit, so that one
rule says which steps a compartment accepts.
<!-- derived: 1.4e6 time constants from core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- derived: 1.4e6 time constants from core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- derived: 1.4e6 time constants from core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->

### The numerical envelope

Every compartment volume and every partition coefficient in the model has a declared *numerical
envelope*. That is the range in which the arithmetic has been checked against a high-precision
evaluation. It runs from 0.01 to 10 000 L for a volume and from 0.001 to 10 000 for a coefficient.
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_VOLUME_L = 10000 -->
<!-- provenance: core/numerical_envelope.py MINIMUM_PARTITION_COEFFICIENT = 0.001 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_PARTITION_COEFFICIENT = 10000 -->

**The envelope is not a supported range.** `docs/INTERFACE.md` § "Supported input ranges" sets out where the model is
claimed to represent a patient. The envelope states only where the arithmetic has been checked,
and how accurate it was found to be. It is set far outside every value the simulator ships with,
so no real parameter set comes near it. The shipped volumes run from 1.222 to 33 L, and the
shipped coefficients from 0.42 to 70. A value inside the envelope can still describe no patient:
a 10 mL lung is inside it and is not a lung.
<!-- provenance: data/patients/reference_adult.json venous_pool_volume_l = 1.222 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.muscle.volume_l = 33 -->
<!-- provenance: data/agents/desflurane.json blood_gas_partition_coefficient = 0.42 -->
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70 -->
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->

#### Every input's range

**Every input to the model has a range that includes its ends.** A value outside its range is
refused when it is created. The table gives each input's range and the code that refuses a value
outside it.

| Input | Range | Refused by |
| --- | --- | --- |
| The breathing circuit's volume, the alveolar gas volume, the venous pool's volume and each tissue group's volume | 0.01 to 10 000 L | `CompartmentVolume` |
| The blood:gas and each tissue:gas partition coefficient, and each tissue:blood coefficient formed from them | 0.001 to 10 000 | `PartitionCoefficient` |
| Fresh gas flow | 0 to 10 L/min | `FreshGasFlow` |
| Alveolar ventilation | 0 to 12 L/min | `AlveolarVentilation` |
| Cardiac output | 0 to 10 L/min | `CardiacOutput` |
| A tissue group's perfusion fraction | above 0, up to 1, the three summing to 1 | `PerfusionFraction` and `PatientCompartments` |
| A tissue group's blood flow | its perfusion fraction of the cardiac output, so 0 to 10 L/min | `BloodFlow` |
| The time step of a compartment stepped on its own | 0.001 s to 86 400 s | `require_compartment_step` |
| A time in the case | a whole number of seconds from 0 to 86 400 s (24 hours) | `CaseInstant` |
| A run's step count | 0 to 86 400, one step for each second | `require_supported_step_count` |
| A partial pressure, as a fraction of one atmosphere | 0 to 1 | `Fraction` |
| The same, as a percent of one atmosphere | 0 to 100 | `Percent` |
| The delivered concentration in the whole model | 0 to 99% | `UptakeEquationSettings` and `AgentUptakeSystem.set_delivered_concentration_percent` |
| Each fraction the whole model is built with | 0 to 0.99 | `AgentUptakeSystem` |
| The state a run starts from, each fraction | 0 to 1, and each cumulative amount of agent 0 to 14 400 L | `require_canonical_state` |
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_VOLUME_L = 10000 -->
<!-- provenance: core/numerical_envelope.py MINIMUM_PARTITION_COEFFICIENT = 0.001 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_PARTITION_COEFFICIENT = 10000 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->
<!-- provenance: core/blood_flow.py MAXIMUM_PERFUSION_FRACTION = 1 -->
<!-- provenance: core/supported_ranges.py MINIMUM_COMPARTMENT_STEP_S = 0.001 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_INPUT_FRACTION = 0.99 -->

One refusal is expected even though every input lies inside its range. Like every refusal inside
the ranges, it is an error from `core/exceptions.py`, never a wrong value. At the hardest
combinations of extreme volumes and coefficients, a run taken in steps is stopped by the
mass-balance check on its first step or within minutes, as
§ "The mass-balance check at the hardest corners" describes below.

**In the whole model, the delivered concentration stops at 0.99 of the ambient pressure, and so
does each fraction the model is built with.** A gas's partial pressure cannot exceed the ambient
pressure, and the model fixes that at one atmosphere, 760 mmHg (`docs/MODEL.md` § "Assumptions"). So no
compartment can hold agent at a fraction above 1. The check on a fraction therefore allows
nothing above 1, and the inputs stop below 1 to leave room for rounding. A dial above 99% is
refused, and the whole model refuses to start with any compartment above 0.99. A computed fraction
is still checked only from 0 through 1, because rounding may put it just above 0.99.
<!-- provenance: core/supported_ranges.py MAXIMUM_INPUT_FRACTION = 0.99 -->

The input limit of 0.99 is `MAXIMUM_INPUT_FRACTION` in `core/supported_ranges.py`. The model
applies it to the amount of agent each compartment holds, because reading a fraction back from
that amount can add a rounding error in the last digit. A venous pool set to 0.99 read back as
0.9900000000000001, and the check does not refuse it for that.
<!-- provenance: core/supported_ranges.py MAXIMUM_INPUT_FRACTION = 0.99 -->

A model of hyperbaric or reduced pressure would keep the limit of 1 on a fraction at that pressure.

The chart checks each fraction it computes before drawing it, so a chart that computes a fraction
above 1 is refused rather than drawn. A chart opened from a state at 1 at the hardest corner
computes one, and no supported setting produces that state. The refusal names the compartment, such as the muscle group, because
a learner sees it as the banner that says why the run halted.

When the chart refuses a state at 1, it raises `SimulationNumericalError`.

Two types in `core/numerical_envelope.py` enforce the envelope:
`CompartmentVolume` and `PartitionCoefficient`. Every compartment, settings record and parameter
file read by `core/parameters.py` uses them. Because every input to `core/` has a range, a
calculation added later works within those ranges, and nobody has to set limits for it.

Both envelope ranges are positive and include their ends, so every product or quotient of two
values inside them is positive, finite and well within a computer's range. A volume times a
coefficient lies between 0.00001 and 10⁸ L.

**The tissue:blood coefficient is checked where it is formed.** It is the tissue:gas coefficient
divided by the blood:gas coefficient. Two coefficients inside the envelope can give a quotient far
outside it, such as 0.001 over 10 000. One function forms the quotient and checks it, by
building it as a `PartitionCoefficient` (`tissue_blood_partition_coefficient` in
`core/numerical_envelope.py`). The agent's parameters (`AgentParameters`) hold both factors, so
they check the quotient again whenever either factor changes. A tissue group (`TissueGroup`)
holds only its tissue:gas coefficient, so the patient's compartments (`PatientCompartments`) check
each group's quotient when the patient is built and when a group is replaced. A group's tissue:gas
coefficient cannot be changed after the group is built.

A tissue group's blood flow has no range of its own. It can only be created as a perfusion
fraction of a cardiac output, so it lies between zero and that cardiac output. A tissue group
stepped on its own takes only a flow created that way, and the venous pool takes the cardiac
output, which is its flow. So neither can be stepped at a flow above the largest supported
cardiac output, or at a flow that is negative or not a finite number.

The state a run starts from has one check (`require_canonical_state` in
`core/governing_equations.py`). Both the definition of a run (`RunDefinition`) and resuming the
live system (`resume_at`) use it. It checks the state's length, that its values are finite, that
the entry fixed at 1 is 1, and that each of the six fractions lies from 0 through 1, by building
each as a `Fraction`. The upper
limit for a fraction is 1, rather than 0.99, because a run's definition and a resumed system both
start from a state that a run passed through, where rounding may have put a fraction just above
0.99. The check also refuses a total of agent delivered or exhausted below zero or above 14 400 L,
the fresh gas of a 24-hour case at 10 L/min. Neither the delivered nor the exhausted fraction can
exceed 1, so no case can move more agent than that. A test in
`tests/unit/test_governing_equations.py` sets each fraction and amount to the nearest storable
value past each limit and expects a refusal.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

#### The tests across the envelope

The sweep in `tests/unit/test_numerical_envelope_sweep.py` has two tests. The first runs every
calculation at 96 extreme combinations of volumes and coefficients, called corners. At each
corner, each volume is at one of its limits, and the two coefficients are at one of the six
corners of the region allowed by their own limits and the tissue:blood quotient's limits. Each
flow is set to zero, to the smallest positive number a computer can hold and to its maximum. The
test steps the whole model once, steps each compartment alone
at its own limits, and predicts every second of a 60 s run in one-second steps. At the three
corners where rounding went furthest,
`test_a_state_at_the_fraction_ceiling_stays_within_one_atmosphere` also predicts every second of
24 hours, at one setting of the flows: no fresh gas, 12 L/min of ventilation and 10 L/min of
cardiac output. Each run washes in
to the 0.99 limit, washes out from it, or sits at it. Stepped alone, a tissue group and the venous pool run at zero flow, at the
smallest positive flow and at the largest supported cardiac output, and each result stays
finite and between its start and its equilibrium.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->

Each result of the first test must be finite. Each fraction must lie from 0 through 1, with no
allowance. What else a result must meet depends on how it was computed.

1. **A predicted run.** Each fraction must also lie at or below 0.99, and the agent balance must
   close, both to within the error bound of the propagators that produced the state
   (`propagator_rounding` in `core/rounding.py`). That bound is 10 times $`2^{s} \cdot 2^{-52}`$
   for the $`s`$ squarings that a step at that corner and those flows actually needs. The 10 is
   `PROPAGATOR_ROUNDING_UNITS`, derived from the arithmetic, so at a corner that needs no
   squarings the bound is ten rounding errors. The worst result, from runs on
   2026-10-26, reached 2.5 times the bound's leading term, $`2^{s} \cdot 2^{-52}`$ for $`s`$
   squarings. The separate 24-hour test holds its predictions to the 0.99 limit in the same
   way, with `run_rounding`, and does not check their agent balance.
2. **One step of the whole model.** Each fraction must lie at or below 0.99 to within the bound
   for 22 squarings, the most that any corner's step needs (`MOST_SQUARINGS` in
   `tests/unit/test_numerical_envelope.py`), whatever the corner needs itself. The agent balance
   is held to the simulator's own check, described next.
3. **A compartment stepped alone.** It is advanced by its own exact solution, not by a
   propagator, so no propagator bound applies. Each amount must lie between its starting value
   and its equilibrium, and the circuit's agent balance must close to within four rounding
   errors.
<!-- provenance: core/rounding.py PROPAGATOR_ROUNDING_UNITS = 10 -->

One step of the whole model must pass the simulator's own mass-balance check, which allows
one part in 10⁹. A step that needs 22 squarings may be refused by that check instead. The test
accepts the refusal only when the imbalance is within the error bound for 22 squarings and the
step was undone. On 2026-11-21 the check refused 76 of the 864 first steps that need 22
squarings, at 8 of the 96 corners, and the largest imbalance was 1.7 parts in 10⁹. Those 8
corners all have the alveolar gas at 0.01 L and blood:gas at 10 000, with the circuit or the
venous pool at 10 000 L. § "The mass-balance check at the hardest corners" below describes these
halts.
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_VOLUME_L = 10000 -->

The second test creates each input in the table at each end of its range and at the nearest value
a computer can store past it, and requires the simulator's own refusal. Setting the model's
starting state puts every compartment at the edge at once, so the first refusal is for the
circuit's fraction, which is checked directly. A compartment that stores an amount is checked to
within the computer's last digit instead.

#### The margin between 0.99 and 1

The gap between 0.99 and 1 must exceed the largest overshoot that a run started at 0.99 computes.
The overshoots below come from runs at all 96 corners, each with the 27 combinations
of extreme flows, for a wash-in to 0.99, a washout from it and an equilibrium at it. Both rows
were computed on 2026-11-21:

| Path | Largest fraction computed from 0.99 | Overshoot above 0.99 |
| --- | --- | --- |
| One step of the whole model | 0.9900000011938722 | 1.2e-9 |
| 86 400 one-second steps, as a preview takes them | 0.9901019652292411 | 1.0e-4 |
<!-- provenance: core/supported_ranges.py MAXIMUM_INPUT_FRACTION = 0.99 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The largest excess is 0.010 percentage points (computed 2026-11-21), the size of the smallest
change the display shows, 0.01 percentage points at two decimals. It is the rounding of each step
added up over 86 400 steps: one step's excess of 1.2e-9, 86 400 times, is 1.0e-4. It arises at a
corner with the alveolar gas, the venous pool and the tissues at 0.01 L, the circuit at
10 000 L, blood:gas at 10 000 and tissue:blood at 0.001. No shipped agent needs a calculation that
hard. No run in the application predicts it. A preview starts from a second that the run has
stepped to, and a run stepped at that corner stops on the mass-balance check at its first step.
At the hardest corners a stepped run stops within seconds, as shown below.
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_VOLUME_L = 10000 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The 0.99 limit keeps even the largest excess inside the ambient pressure. The limit is far above
every shipped vaporizer maximum, the highest being desflurane's 18%, so no shipped run is affected.
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->

The 0.99 limit leaves a margin of 0.01, about 100 times the largest excess. Pushing a computed
fraction back to 1 would hide an error the size of the largest excess instead of limiting it. The
limit belongs to the model, not to one agent's vapour pressure, so a later gas delivered at a high
fraction does not need a new limit.

#### Squarings, and why the limits were kept

The accuracy of each step's calculation sets the envelope's bounds, which are
far narrower than the products and quotients alone would allow. That calculation
(`core/matrix_exponential.py`) halves the interval until it is short, then doubles the result
back up. Each doubling, called a squaring, can double the rounding error, so the number of
squarings sets the accuracy ("What it costs" in that module). The fastest rate in the model sets
how many are needed.

**At every corner of the envelope, the one-second step needs at most 22 squarings.** That is a
factor of $`2^{10}`$ below the cap of 32. The count was taken on 2026-11-21 over 2,560 corners,
with every flow at zero or at the top of its supported range and cardiac output divided among
the tissues in four ways. A shipped agent's step needs 2 squarings at its default flows and 3 at
the widest supported flows. A test checks the count of 22 at the 128 corners that have every
flow at its maximum, and the count of 19 that one calculation over 24 hours needs for shipped
sevoflurane (`test_the_step_needs_at_most_22_squarings_at_any_envelope_corner` in
`tests/unit/test_numerical_envelope.py`).
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The table gives the corners that matter, each compared with a calculation to 70 digits on
2026-11-21. In each row, the inputs not named are at the shipped values, and every flow is at the
top of its supported range. "Step error" is the worst error, as a share, in any part of one
step's calculation. "After 24 h" is the worst error, as a share, in a wash-in from zero after
86 400 steps, against the exact state at 24 h.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

| Corner | Fastest rate (1/s) | Squarings in one step | Step error | After 24 h |
| --- | --- | --- | --- | --- |
| Shipped sevoflurane | 0.136 | 3 | 2.2e-15 | 7.6e-11 |
| Alveolar gas 0.01 L, blood:gas 10 000, every tissue:blood 1 | 1.67e5 | 22 | 1.3e-9 | 4.8e-5 |
| Alveolar gas 0.01 L, blood:gas 10 000, tissue:blood as shipped | 1.67e5 | 22 | 1.2e-9 | 4.1e-5 |
| Every volume 0.01 L, blood:gas 10 000, every tissue:blood 0.001 | 1.67e5 | 22 | 9.3e-10 | 4.0e-5 |
| Vessel-rich group 0.01 L, its tissue:blood 0.001 | 1.27e4 | 18 | 1.2e-10 | 5.0e-6 |
| Circuit 0.01 L | 36.7 | 10 | 3.4e-13 | 1.5e-8 |
| Venous pool 0.01 L | 16.7 | 9 | 1.5e-13 | 5.3e-9 |
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->

The third row keeps the tissue groups at their shipped tissue:blood coefficients with blood:gas
at 10 000, which makes each tissue:gas coefficient larger than 10 000. A settings record can build
those settings, but no parameter file can.

**The limits were chosen for a step of 0.1 s, and they were kept for the one-second step.** They
were chosen on 2026-10-25, when a run took a step of 0.1 s. The criterion was that at every
corner, the step should need no more squarings than the shipped parameters already need for one
calculation over 24 hours. That number is 19, for sevoflurane at the widest supported flows, and
the 0.1 s step needed at most 19. A smallest volume of 0.001 L was refused then. With the
alveolar gas at 0.001 L, the hardest corner needed 22 squarings, its step error was 1.7×10⁻⁹
against 5.8×10⁻¹¹ at 0.01 L, and over a 24-hour run that error grew to 0.049% of the state.
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The one-second step needs those 22 squarings at the smallest volume of 0.01 L, three more than
the criterion allowed. The limits were kept on 2026-11-21 all the same, for four reasons:
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->

1. What the criterion protected is the error of a run after 24 hours. At the hardest corner that
   error is 0.0048% of the state. It is twice the 0.0025% of the 0.1 s step, and a tenth of the
   0.049% that refused a smallest volume of 0.001 L. A one-second step has more squarings than a
   0.1 s step, but a day holds a tenth as many steps.
2. The smallest volume is 122 times below the smallest shipped volume, and the mass-balance
   check halts a run at the hardest corner after 11 s.
3. Raising the smallest volume to 0.1 L would bring the count back to 19. It would also refuse
   a volume only 12 times below the smallest shipped one.
4. Nothing a learner sees depends on the choice.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**No stored state comes from a calculation that spans more than one second.** A run and a
branch take one-second steps, and the chart draws the states the run stored. The calculation
needs more squarings of a matrix for a longer interval or faster rates, and each squaring can
double the rounding error. A one-second step needs at most 22 squarings at the hardest corner,
below the limit of 32 at which `core/matrix_exponential.py` refuses a propagator. A preview takes
one-second steps for its first hour, then one calculation for each chart column. For a shipped
agent at the largest supported flows, a column of 579 s, the widest a chart draws, needs 12
squarings (measured 2026-11-21).

**A patient profile or agent near the volume or coefficient limits would need those limits
rechecked.** The 0.01 L volume limit was set at the adult supported flows, and a patient profile
with much smaller volumes would bring much smaller flows with it. A profile with a volume within
a factor of ten of that limit would need this measurement repeated at its own flows. So would an
agent with a coefficient within a factor of ten of either coefficient limit.
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->

#### The mass-balance check at the hardest corners

**At the hardest corners of the envelope, the mass-balance check halts a run that advances in
steps.** After every step, the check in § "Mass-balance identity" requires the agent
delivered, exhausted and stored to agree within one part in 10⁹. At 22 squarings, the bound on
one step's rounding error is 9.3 parts in 10⁹, which is above that tolerance. So the check can
refuse the first step, as it does at 8 of the 96 corners in the test above. Where the first step
passes, the unaccounted agent grows with each step until it exceeds the tolerance. Then the step
is undone, and the run ends with an error. On 2026-11-21,
sevoflurane was run at the widest supported flows, with every tissue:blood coefficient set to 1:

| Alveolar gas | Blood:gas | The mass-balance check halted the run at |
| --- | --- | --- |
| 0.01 L | 10 000 | 11 s |
| 0.01 L | 100 | 765 s |
| 1.0 L | 10 000 | 904 s |
| 0.01 L | 12 | no halt within 1 h |
| 2.5 L | 100 | no halt within 1 h |
| 0.1 L | 1.3 | no halt within 1 h |
<!-- not-restated: 2.5 L -->
<!-- not-restated: 1.3 -->
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->

A run that exceeds the mass-balance tolerance
(`AGENT_ACCOUNTING_RELATIVE_TOLERANCE`) halts with `AgentSimulationValidationError`.

Inside the envelope, a run either matches the high-precision calculation to the limits in the
earlier table with the "After 24 h" column, or is refused with an error. That column shows one
step's calculation repeated 86 400 times, which is not a run that the model completes at the
hardest corners. Even with 0.01 L of alveolar gas, a run did not halt within an hour at a
blood:gas coefficient of 12, as high as any volatile agent's.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->

**The mass-balance tolerance stays fixed at one part in 10⁹.** A tolerance that grew with the
number of squarings would end the halts above, but it would also loosen the check where learners
run. A shipped agent's step needs 2 squarings at its default flows and 3 at the widest supported
flows. Over 24 h, a correct run's worst error was 9.8 parts in 10¹², about a hundredth of the
tolerance. That run was sevoflurane at its highest dial setting, 8%, with 0.5 L/min of fresh
gas, 12 L/min of ventilation and 10 L/min of cardiac output (computed 2026-11-21).
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->

**The tolerance is not the sum of the worst-case rounding of every step.** For a shipped agent's
longest run, that sum is 1.5 parts in 10⁹. The run is 24 h long, and each of its steps needs at
most three squarings. So the sum is one and a half times the tolerance, and the measured error
above is the check on it. For the same 24 h at the earlier step of 0.1 s, which needed no
squaring, the sum was 1.9 parts in 10⁹. So the one-second step did not move the sum further
above the tolerance.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

One step's rounding is bounded by $`10 \cdot 2^{s} \cdot 2^{-52}`$, where $`s`$ is the number of
squarings the step needs and 10 is the factor that § "How far a computed value can be from the
exact one" derives. At $`s = 22`$ that is 9.3e-9. The mass-balance check compares the whole
run's residual, so a rigorous
tolerance would sum that bound over every step (`run_rounding` in `core/rounding.py`). Over the
86 400 steps of a 24 h run, the sum is 1.5e-9 at $`s = 3`$ and 7.7e-10 at $`s = 2`$. At
$`s = 0`$, the sum was 1.9e-9 for 24 h at the earlier step of 0.1 s and 1.9e-7 at the 1 ms step.
A tolerance widened only by what the
squarings add would be about $`10 (2^{s} - 1) 2^{-52}`$ per step, summed over the run, which is
exactly $`10^{-9}`$ wherever $`s = 0`$.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- not-restated: 1 ms -->

The tolerance was fixed on 2026-10-31, when a run could also take steps of 1 ms. The sum for
24 h of those steps was 1.9 parts in 10⁷. That is about 190 times looser than one part in 10⁹,
so a real accounting error could have passed on a long run that a learner could reach. A
tolerance widened only by what the squarings add would end the halts at the hardest corners. It
has not been built (`PL-TLKY`).
<!-- not-restated: 1 ms -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**A test shows when to revisit the mass-balance tolerance.** It runs each shipped agent with the
patient and machine that the application uses. It sets each flow at either end of its supported
range, and requires that the step needs at most three squarings. It also requires that the sum
for the longest run is no larger than the sum at the 0.1 s step. A patient
profile with faster rates, such as a small patient, fails the test on the day the profile ships.

The test that fails when a step needs more than three squarings is
`test_every_shipped_agent_steps_with_at_most_three_squarings_at_any_supported_setting` in
`tests/unit/test_numerical_envelope_sweep.py`. Its failure message says to set the tolerance
again from the sum for the longest run.

#### Volumes outside the envelope

**The model no longer accepts some volumes that this document describes.** They are the 0.005 L
alveolar compartment in `docs/INTERFACE.md` § "What is not bounded this way", every volume below 0.01 L in the
paragraphs that follow, and every circuit volume above 10 000 L. Each is outside the numerical
envelope (§ "The numerical envelope"). The results at these volumes are kept because they show
what the propagator's own refusals do when a matrix reaches them by another route.
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_VOLUME_L = 10000 -->

**At tiny alveolar volumes, a run eventually halts or is refused.** The 2026-09-06 results in
`docs/INTERFACE.md` § "What a wrong volume would be wrong for" were extended to smaller volumes, at the step of
0.1 s that a run then took. At an alveolar volume of $`10^{-8}`$ to $`10^{-10}`$ L, the mass-balance check halted the run
with `AgentSimulationValidationError`. From $`10^{-11}`$ L down, the propagator was refused before
any arithmetic. Down to $`10^{-308}`$ L, it was refused because it would need more than 32
squarings (described below). Below that, it was refused because scaling the matrix down overflows,
and then the matrix itself overflows. Both the halt and the refusal are the required "obvious
failure rather than a plausible-looking number", but they arrive by accident of arithmetic.
Neither is a limit that this document declares, and neither may be treated as one. They sit far
below any volume a caller would pass by mistake, and they say nothing about the physiological
question that `docs/INTERFACE.md` § "What a wrong volume would be wrong for" asks. Circuit volume has no such point.
Runs with circuit volumes up to $`10^{300}`$ L passed the mass-balance check throughout.

**A mass-balance check cannot catch a failure that wipes out every term it compares.** Before the
refusals described below existed, an alveolar volume of $`10^{-300}`$ L turned the propagator
into the zero matrix. The propagation function (`propagate()`) then returned all zeros. Every
total had been wiped out together, so the mass-balance identity compared $`0 + 0 - 0 - 0`$, and
zero does balance zero. No volume that can now be built reaches this, and a test reaches it only
with a matrix built for the purpose. Look for the same weakness wherever a check compares
quantities that one failure can affect together.

So the matrix exponential module refuses a zero propagator. $`\exp(A\,\Delta t)`$ can be inverted
for every finite $`A`$, because its determinant is $`e^{\operatorname{tr}(A)\Delta t}`$. A zero
result can therefore only be a floating-point artifact. The module scales the matrix's norm down
to the bound that the series needs, and it also refuses a step when that scaling overflows. That
case would otherwise raise a bare `OverflowError` at $`10^{-309}`$ L, outside the error types in
`core/exceptions.py` that a caller relies on. Both refusals reach the caller as
`SimulationNumericalError` through the uptake system's step (`AgentUptakeSystem.advance()`), and
the step is rolled back. The constant state (`governing_equations.UNIT_STATE`) is the state
variable that no step changes. A matrix that carries it cannot produce the zero matrix at all, so
the model now stops those volumes earlier, at the limit on squarings described below. The scaling
refusal still fires first wherever the scaling overflows.

At that step of 0.1 s, the propagator was tried at every power of ten from $`10^{0}`$ to
$`10^{-323}`$ L. It was returned at the 11 volumes from $`10^{0}`$ to $`10^{-10}`$ L, each with the
constant state's row exact. The other 313 were refused before any arithmetic. A single entry is
still returned as 0.0 when it is too small for any double, such as `exp(-0.5 * 3600)`, and that is
correct. Such a single zero is what distinguishes a decayed entry from a wiped-out matrix.

**A limit on the squarings closes the last failure in this family.** At very small volumes,
the propagator can stay finite and nonzero while the constant state's row drifts. No interval may
change that row, which is why the constant state's row in $`A`$ is empty. The shift that the
module applies to the matrix before summing its series lets error in, and the squarings amplify
it. After $`s`$ squarings, the worst entry's relative error is $`c\cdot2^{s}\cdot2^{-52}`$. On
2026-10-03, $`c`$ was between 0.6 and 2.7 at every power of ten tested against a high-precision
calculation of the same exponential, from those needing no squarings to those needing 45. So
every state whose own rate is small next to the shift drifts the same way. Two changes close the
failure:

1. The constant state's row is set to the identity matrix's row before the squarings, which keep
   it exact to the last bit. So no step changes the constant state in floating point, as in the
   algebra.
2. A propagator that needs more than 32 squarings is refused before any arithmetic, because
   beyond that the error bound exceeds one part in a million.

The first change alone is not enough, because with the constant state's row exact a wrecked
matrix is no longer zero, so only the limit refuses it. A regression test in
`tests/unit/test_agent_simulation_validation.py` covers a case that the mass-balance check passed
with every propagator entry wrong.

The matrix exponential module (`core/matrix_exponential.py`) computes the propagator
$`\exp(A\,\Delta t)`$ for the system matrix $`A`$ over an interval $`\Delta t`$. The function that
returns the propagator (`matrix_exponential`) refuses a stretch that needs more than 32
squarings with `SimulationConfigurationError`.

Tests of the matrix exponential module still trigger the propagator's own refusals, with a matrix
built to match (`tests/unit/test_matrix_exponential.py`).

### How far a computed value can be from the exact one

Every value the model computes is rounded to a 64-bit number, so it differs slightly from the
exact value of its equation. The table gives the largest difference that the model allows in each
comparison it makes. None of them reaches a displayed digit. Over a shipped agent's longest
supported run, 24 h, the bound on a reading is 1.5 parts in 10⁹ of the reading, and the readouts
show a percentage to two decimals.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

| What is compared | Allowed difference | Kind |
| --- | --- | --- |
| The state after one step, against the exact solution | $`10 \cdot 2^{s} \cdot 2^{-52}`$ of the largest fraction in the run, where $`s`$ is the number of squarings the step needs. With no squarings that is 2.2e-15, and with the three that a shipped agent's step needs at most it is 1.8e-14. | Bound |
| The state after $`n`$ steps, against the exact solution | $`n`$ times the allowance for one step | Bound |
| A running total of delivered or exhausted agent, against the exact sum of its step amounts | $`2^{-51}`$ of the total, which is 4.4e-16 | Bound |
| Agent held, delivered and exhausted (§ "Mass-balance identity") | One part in 10⁹ of the agent handled, or 1e-12 L | Fixed |
| $`F_A/F_I`$ above 1 in a run that is still washing in (`docs/INTERFACE.md` § "F_A/F_I as a displayed ratio") | 1e-6 | Fixed |
| A reading at the height of a MAC target (`docs/INTERFACE.md` § "Halting on a marked crossing") | 1e-5 of the height | Fixed |
| The tissue perfusion fractions, against a sum of 1 (`docs/MODEL.md` § "Blood flow to the tissue groups") | 1e-12 | Fixed |
| The tissue blood flows, against cardiac output | One part in 10⁹ of cardiac output, plus 1e-12 L/s | Fixed |
| A count of ticks on the chart's percent axis, against a whole number | 1e-9 of the count | Fixed |

A bound follows from the arithmetic, and a test fails when a result exceeds it. The factor of 10
in the first row is derived too. It counts every rounding in one step at its largest possible
size, and lets each squaring double the error it receives. The count gives at most 9.13 times
$`2^{s} \cdot 2^{-52}`$, and 10 is that rounded up. The largest fraction in the run includes the
fraction that the vaporizer delivers. A measurement checks that
the bound is not far above what happens. On 2026-11-11 and 2026-11-14, 480 000 steps were drawn
across the numerical envelope, and one corner was stepped from 400 opening states. The largest
error was 3.9 times $`2^{s} \cdot 2^{-52}`$, at that corner, which is about 40% of the bound.
A fixed allowance is a chosen number, far above the rounding that
was measured and far below a displayed digit. The section named in each row gives its
measurement.

**The bound for $`n`$ steps is the sum of the steps' bounds.** The other candidate grows as the
square root of $`n`$. It holds where the rounding errors are independent and average zero, and a
run that repeats one step $`n`$ times meets neither condition. A state held at equilibrium in a
10 000 L tissue drifted by 1.6e-12 over 4 308 steps on 2026-11-11, which is 38 times the
square-root figure. The five steps with the largest errors in the same day's measurement were
each repeated 2 000 times, and the error after $`n`$ steps stayed at $`n`$ times the error of
one.
<!-- provenance: core/numerical_envelope.py MAXIMUM_VOLUME_L = 10000 -->

- Higham and Mary show that the square-root bounds hold "under the assumption that rounding
  errors are independent and of zero mean", and give "two cases where Model 2.1 is invalid and
  the probabilistic bound does not hold. In the first case the rounding errors have nonzero mean
  and in the second case they are dependent" (Higham NJ, Mary T. A new approach to probabilistic
  rounding error analysis. SIAM J Sci Comput 2019;41(5):A2815-A2835. doi:10.1137/18M1226312,
  sections 5 and 4.2).
- Connolly, Higham and Mary describe a sum that stops changing under round to nearest: "This
  leads to necessarily negative rounding errors", and the error then grows in proportion to
  $`n`$ (Connolly MP, Higham NJ, Mary T. Stochastic rounding and its probabilistic backward
  error analysis. SIAM J Sci Comput 2021;43(1):A566-A585. doi:10.1137/20M1334796, section 7).
- Croci et al. say that the two assumptions "are often satisfied in practice, but it is easy to
  construct examples where either of the assumptions fails and the backward error almost attains
  the worst-case bound" (Croci M, Fasi M, Higham NJ, Mary T, Mikaitis M. Stochastic rounding:
  implementation, error analysis and applications. R Soc Open Sci 2022;9:211631.
  doi:10.1098/rsos.211631, section 6.1).
<!-- not-restated: 2.1 -->

The first two papers were read on 2026-11-11 as their MIMS EPrints, 2018.33 and 2020.12, in the
passages quoted. The third was read the same day in the full text at PubMed Central (PMC8905452),
in section 6.1. None of them analyses one propagator applied $`n`$ times, so the measurement is
the evidence for the summed bound here, and the papers are the reason it was expected.

**The agent balance does not use the summed bound.** It keeps its fixed limit of one part in
10⁹, for the reasons that § "The numerical envelope" gives. The summed bound for a shipped
agent's longest run is one and a half times that limit. The
bound is the most that rounding can do anywhere in the numerical envelope, and the shipped agents
stay far inside it. A correct 24-hour run of a shipped agent left a residual of at most 9.8
parts in 10¹².

`core/rounding.py` defines every figure in the table, and each comparison in
`core/` and `app/` reads its allowance from there. `propagator_rounding` is the bound for one
step, `run_rounding` the bound for $`n`$ steps, and `RUNNING_TOTAL_ROUNDING` the bound for a
running total. `tests/unit/test_rounding.py` checks each
figure and that no other module in `core/` or `app/` defines an allowance.
Two tolerances for the shares of a window that its areas take stay in `layout/`.
`tests/unit/test_generated_runs.py` holds generated runs to the bounds after every action, and
`tests/unit/test_numerical_envelope_sweep.py` holds one step from each corner of the envelope to
the bound for one step. The factor of 10 is `PROPAGATOR_ROUNDING_UNITS`, whose docstring gives
the derivation. It counts the roundings with the standard model of floating-point arithmetic and
its bound on a product of rounding factors (Higham NJ, Mary T, MIMS EPrint 2018.33, eqs. 1.1 and
1.2, pp. 2-3, and Lemma 2.2, p. 4), and the error of Python's compensated `sum` (Ogita T, Rump SM,
Oishi S. Accurate sum and dot product. SIAM J Sci Comput 2005;26(6):1955-1988. Proposition 4.5,
read in the authors' copy). It assumes that the C library's `exp` is within one unit in the last
place, which glibc states. It also assumes that the fraction rows create agent at a rate $`r`$
with $`r\,\Delta t \le 2^{-9}`$. The equations create none, and the check that the tissue flows
sum to cardiac output keeps $`r\,\Delta t`$ below 1.5e-3 over 24 h. The errors are measured in the row sums of the propagator's fraction
rows, with the forcing column divided by the delivered fraction. Every number is nonnegative after
the shift, so the relative bounds add without cancellation. The factor was a measured margin of 3
until 2026-11-11, when a review found a step inside the envelope with an error of 3.4 times
$`2^{s} \cdot 2^{-52}`$, and a measured margin of 8 until 2026-11-14. `tests/unit/test_rounding.py`
derives the bound again from the matrix exponential module's constants, holds 200 steps drawn
across the envelope to it, and recomputes the four worst steps found against a 50-digit
calculation, requiring them to pass 3 and stay inside 10.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- not-restated: 1.1, 4.5 -->

## Reasonably foreseeable misuse, and the hazards the presentation carries

For each way a reader could be misled, the table below gives what prevents it
and the tests that check that safeguard, or says plainly that no test does.
`docs/MODEL.md`, `docs/INTERFACE.md` and the rest of this document argue
forward from each decision, which finds the mistakes someone thought to look
for. This table works back from each way a reader could be misled, which finds
the others.

The right-hand column lists only tests that exist. A check fails when a test
named anywhere in this document matches no existing test. A reviewer still has
to judge whether each test is any good.

| A reader could be misled into | What stops it | Tested by |
| --- | --- | --- |
| reading a run as a prediction for a real patient whose data was entered into it | the use statement stays in view. It is the disclaimer at the foot of the window. The simulated patient is always the built-in reference adult. Cardiac output and ventilation are teaching controls, and a learner can set either one to a value measured in a patient. Only the use statement stops a learner reading that run as a prediction for that patient (§ "What keeps a real patient's data out of a run") | `test_the_educational_disclaimer_says_what_the_tool_is_not`, `test_the_dashboard_carries_the_educational_disclaimer`, `test_the_region_and_the_use_disclaimer_stay_in_the_viewport`, `test_every_run_simulates_the_shipped_reference_adult` |
| reading a correct concentration as belonging to a different agent | agent colour is never the only cue. The agent name is always visible in every top-level window, within the limit stated in `docs/INTERFACE.md` § "Minimum displayed outputs" -> "What this list requires once the layout is the reader's". A separate tool checks the ISO 5360 agent colours and the text colour that stays readable on each (`tools/contrast_check.py`, which reads the colours from `src/anesthesia_sim/app/theme.py`) | `test_agent_dropdown_options_pair_every_color_with_the_agent_name`, `test_every_agent_has_render_objects_in_its_own_identification_color`, `test_the_agent_name_stays_legible_while_the_run_disables_the_selector` |
| reading a run halted by a failure as one the user paused | a halt has its own status words, and the two failure modes have different words. The status word, the transport controls and the banner are set from the run's status alone, never from a compartment value. A halted run therefore still shows as stopped, and does not offer Pause, even when its values cannot be read. When a run halts before any of it has been drawn on screen, its banner says so, instead of claiming that a step was rolled back | `test_refresh_view_reports_a_failed_run_as_stopped_not_paused`, `test_refresh_view_reports_the_supported_run_length_as_stopped_not_failed`, `test_a_halt_is_shown_when_the_snapshot_itself_is_refused`, `test_a_halt_is_stated_from_the_run_status_alone`, `test_a_halt_no_frame_was_drawn_for_is_worded_as_one_rather_than_as_a_failed_step` |
| reading a run that a mark stopped as one the learner paused, while two runs are compared | the status word reads "Paused — stopped on your mark". While two runs are compared, the branch control hides its own "stopped on your mark", so this status word is the only cue. A failure, or reaching the supported run length, overrides this word. A MAC target's row reads "reached" from its first crossing on. A new branch reads "Paused" at the instant it starts from its parent run, though it carries the parent's halt record, because no step of the branch stopped it | `test_a_halt_on_a_mark_is_told_apart_from_a_pause_during_a_comparison`, `test_a_branch_opened_on_a_mark_crossing_is_not_said_to_be_stopped_by_it`, `test_a_run_a_mark_stopped_is_not_worded_as_the_learner_s_own_pause` |
| reading a run whose Reset the model refused as one still running, or as one that was reset | a refused Reset leaves the run exactly as it was, and the interface halts the run and states the halt (`docs/INTERFACE.md` § "Reset behavior") | `test_a_reset_the_core_refuses_halts_the_run_visibly`, `test_a_reset_the_core_refuses_leaves_the_run_exactly_as_it_was`, `test_a_refused_reset_names_the_way_out_in_the_banner`, `test_a_tissue_flow_mismatch_is_stated_in_litres_per_minute` |
| comparing readouts with a chart that was drawn from different settings | the readouts come from the model's steps, and the chart from the recorded settings of the run. Before each step, the model's settings are compared with the recorded ones. If a setting reaches the model without being recorded, the run halts on the last step on which the two agree, and a banner says why. Reset then starts a new run from the model's settings. A change recorded after such an unrecorded one brings the record back into line with the model without halting the run. The interface never changes a setting without recording it | `test_a_setting_written_onto_the_core_past_the_controller_refuses_the_next_step`, `test_a_setting_written_onto_a_branch_s_core_past_its_controller_refuses_its_next_step`, `test_reset_after_a_setting_written_past_the_controller_runs_at_that_setting`, `test_a_run_whose_core_setting_moved_past_its_controller_halts_on_the_last_recorded_step` |
| reading the agent selector or a slider as a control that took effect, when it was used on a run whose values cannot be read | if reading the run's values fails while the selector or a slider is in use, the run halts and the halt is stated from the run's record, so the failure cannot pass unseen. The selector goes back to the agent that record names. The banner still names Reset as the way to recover, unless a refused Reset has left its own instructions. The controls stay usable on a halted run, because locking them would show the agent selector as disabled. A slider moved on a run that has already stopped is refused, as the row on values from different steps says | `test_an_agent_change_on_a_halted_run_restates_the_halt`, `test_a_slider_moved_on_a_run_whose_snapshot_refuses_halts_it` |
| reading the value printed above a dial whose drag halted the run as the value the run holds | once the halt's banner is written, every dial is set from the run's record (`SimulationController.record()`). The record gives the agent and the four settings in force, and takes them from the settings the compartments hold, not from any compartment value. The label above the dragged dial therefore shows the value that both the dial and the run hold. A run whose values cannot be read draws no new screen that could rewrite the label | `test_a_drag_that_halts_the_run_leaves_its_label_on_the_dial`, `test_a_halt_is_stated_before_its_dials_are_written` |
| reading a value under a label, a 1 MAC divisor or a verdict that describes a different step of the run | each value and what qualifies it come from one step, and values a halt leaves stale are withheld. `docs/INTERFACE.md` § "Every value and what qualifies it come from one step" lists the groups and the cases | `test_every_value_and_its_qualifiers_on_screen_come_from_one_state`, `test_a_halt_after_an_agent_change_shows_no_mac_multiple_beside_another_agent_s_1_mac`, `test_the_accounting_panel_reports_the_failure_after_an_accounting_halt`, `test_a_setting_changed_on_a_halted_run_is_not_shown_as_the_setting_its_values_ran_under`, `test_a_setting_refused_at_the_supported_run_length_names_a_branch_only_while_one_can_be_taken`, `test_a_halt_that_no_frame_draws_after_the_run_started_over_says_its_readouts_are_withheld`, `test_a_stopped_run_refuses_every_setting_and_records_nothing` |
| believing a setting above the vaporizer maximum was simulated | such a setting is **rejected, not capped**, so no run continues on a value the user did not choose. The maximum itself is accepted by the circuit and by the record of settings a run is built from. That record carries the maximum beside the dial setting | `test_rejects_delivered_concentration_above_the_vaporizer_maximum`, `test_explicit_delivered_concentration_above_the_agent_max_is_rejected`, `test_accepts_delivered_concentration_exactly_at_the_vaporizer_maximum`, `test_rejects_a_dial_above_the_vaporizer_maximum`, `test_a_run_cannot_open_or_change_under_a_dial_above_the_vaporizer_maximum` |
| reading a displayed value as resolved to its last digit | the number of decimals shown is a recorded choice within a justified range. Only the display rounds. The model keeps the precision that the display discards | `test_the_model_keeps_precision_the_display_throws_away`, `test_concentration_decimals_are_a_choice_within_a_recorded_band` |
| reading a control mark on the timeline as a measurement | the timeline labels its marks "Settings only — not a measurement." | `test_the_interface_says_a_control_mark_is_an_input_not_a_measurement` |
| reading a modelled compartment value as a measured one | the readout section states, beside its values, that they are model outputs and not measurements (`INTERPRETATION_DISCLAIMER_TEXT`; `docs/INTERFACE.md` § "The statement that the readouts are model outputs"). The chart's hover names every value it reports as modelled (`docs/INTERFACE.md` § "The chart's hover readout: what the tooltip may show") | `test_the_interface_says_the_readouts_are_model_outputs_not_measurements`, `test_the_readouts_say_they_are_model_outputs_beside_the_values`, `test_the_hover_reports_the_drawn_state_through_the_formatters` |
| reading one compartment's concentration as another's where two traces are drawn on top of each other | the compartment is named in text on every value line. The hover reports every compartment whose drawn point at the pointer's instant is inside the hover radius, each under its own name. It does not pick the nearest trace for the reader (`docs/INTERFACE.md` § "When more than one trace is within reach"). This matters because the top of the percent axis is fixed at 3 MAC for every agent (`CHART_AXIS_TOP_MAC`). On that axis, with the chart at its preferred height and the reference adult at the opening ventilation, cardiac output and fresh gas flow, the fat trace moves less than 4 px over its whole first hour at a 1 MAC dial, and less than 12 px at the agent's vaporizer maximum. Raising any of those three settings makes fat rise faster and spreads its trace further. At those settings, two fat traces, from two runs or two dials, are drawn closer together than the hover radius, and no pointer position can pick one out from the other (`docs/INTERFACE.md` § "MAC multiples as a display unit") | `test_two_compartments_within_one_hover_radius_answer_under_their_own_names`, `test_a_contended_hover_names_no_run_while_only_one_is_drawn`, `test_at_opening_settings_fat_first_hour_spans_under_4_px_at_1_mac_and_12_px_at_vaporizer_maximum` |
| comparing two compartments of one run in one hover box as values from one instant, when the box took them from different instants | every compartment of one run is reported at the run's drawn instant nearest the pointer in time. So the instant that labels a value depends only on the pointer's position along the time axis, and the pointer's height decides only which traces are in reach (`docs/INTERFACE.md` § "The instant each value is reported at") | `test_every_compartment_of_one_run_answers_at_one_instant`, `test_a_vertical_hand_movement_never_moves_the_instant_a_hover_reports`, `test_a_trace_answers_only_where_its_point_at_the_named_instant_is_in_reach` |
| reading the hover's value as a live readout after the pointer has left the plot | the hover box shows only while the pointer is over the plot (`docs/INTERFACE.md` § "When the hover readout appears"). It closes as soon as the pointer leaves, and no later screen update brings it back. A box left open would change with every screen update, so its values would climb while a run plays, at an instant the reader is not looking at | `test_the_hover_hides_when_the_pointer_leaves_and_a_later_frame_does_not_bring_it_back` |
| reading one run's displayed value, or the record of what was changed on it, as the other's while two are compared | while more than one run is drawn, every place that shows a value, or the record of what was changed, names its run in text. `docs/INTERFACE.md` § "Naming the run in a comparison" lists the seven places | `test_the_hover_names_the_run_only_while_more_than_one_is_drawn`, `test_two_runs_within_the_hover_radius_answer_under_their_own_names`, `test_a_small_pointer_movement_never_swaps_which_run_the_hover_answers`, `test_the_wash_in_state_and_off_scale_lines_name_their_run`, `test_a_lone_run_leaves_the_shared_chart_lines_unnamed`, `test_each_run_s_unmarked_changes_line_is_named_while_runs_are_compared`, `test_the_sidebar_panels_name_the_run_they_record`, `test_a_lone_run_leaves_the_sidebar_panel_headings_unnamed`, `test_the_halt_and_refusal_banners_name_their_run`, `test_a_halt_stated_without_a_frame_still_names_the_run_it_stopped`, `test_a_lone_run_leaves_the_notice_banner_unnamed`, `test_hidden_notice_banners_take_no_height`, `test_the_schematic_follows_its_run_through_a_reset_an_agent_change_and_a_comparison`, `test_the_panel_follows_its_run_through_an_agent_change_and_a_comparison` |
| reading a preview of a dragged setting as part of the run that happened | the preview is drawn only while the slider handle is held, inside a tinted region with a label saying the value is not applied, and the hover never reports from it (`docs/INTERFACE.md` § "A preview of an unapplied setting") | `test_a_held_thumb_previews_the_setting_without_applying_it`, `test_a_preview_is_drawn_only_inside_its_region_with_its_label`, `test_the_hover_never_answers_from_a_preview` |
| reading a cost as a figure the project supplies, or as computed at a price other than the one it used | the project supplies no price. A cost is shown only beside the two numbers it multiplied, the liquid volume and the price per millilitre. The volume is shown in whole millilitres and the cost is computed before rounding, so the product of the two numbers shown can differ from the cost by up to about half a millilitre's price. The readout says that they are rounded. Beside them are the bottle price, currency and date that the price came from, and words saying that the price is the reader's (`docs/INTERFACE.md` § "A cost at the reader's price") | `test_no_cost_is_shown_until_the_reader_sets_a_price`, `test_the_cost_is_the_delivered_liquid_times_the_bottle_price_over_the_bottle_volume`, `test_the_displayed_cost_reproduces_gas_man_s_printed_costs`, `test_the_cost_is_computed_from_the_unrounded_figures_not_the_ones_shown`, `test_each_run_is_priced_at_its_own_agent_s_price`, `test_no_cost_is_shown_where_one_cannot_be_trusted` |
| reading a cost computed from a price entered in the wrong form: a price per millilitre typed as the bottle price, a bottle volume typed in litres or as a count of bottles, the price and the volume swapped, or a price in another currency | the price is entered as a bottle price and a bottle volume, and the volume field names its unit, millilitres of liquid. The readout shows the price per millilitre of liquid that the two give. The first mistake makes that price 100 to 250 times too low, and the second makes it 100 to 1000 times too high. A swap shows only where price and volume differ widely. At Gas Man's default sevoflurane price, a swap changes the cost by only 8 %. The currency is stored and shown as its three-letter ISO 4217 code, never as a bare "$" (`docs/INTERFACE.md` § "A cost at the reader's price") | `test_an_entry_that_is_not_a_plain_positive_price_is_refused_with_its_reason`, `test_a_refused_entry_changes_nothing_and_says_why`, `test_a_price_per_millilitre_is_shown_to_four_figures_in_millilitres_of_liquid`, `test_a_currency_that_is_not_three_capital_letters_is_refused` |
| reading a container's fill height, or its filled area, as the amount of agent it holds | a container's height shows the compartment's tension on the concentration chart's own scale, and its amount is printed beside it and on a share bar (`docs/INTERFACE.md` § "The compartment schematic: what its heights, amounts and share bar assert") | `test_a_container_s_height_is_its_tension_and_not_its_amount`, `test_fat_s_share_grows_through_the_first_hour_while_its_container_stays_nearly_empty`, `test_the_share_bar_is_painted_to_each_share_and_named_in_text`, `test_the_circuit_fills_to_its_closed_form_tension_on_the_chart_s_scale`, `test_a_tension_above_the_chart_s_top_fills_the_container_and_keeps_its_value` |
| reading an amount of agent vapour as millilitres of liquid, or a liquid-equivalent amount as vapour, which misreads it by a factor of about 180 to 210, depending on the agent | no panel prints a bare "mL" beside an agent amount: every amount says vapour or liquid (`docs/INTERFACE.md` § "The compartment schematic: what its heights, amounts and share bar assert") | `test_no_agent_amount_is_printed_with_a_bare_millilitre_unit`, `test_the_delivered_agent_is_shown_at_its_derived_precision_with_its_unit_named`, `test_patient_inputs_reach_the_drawn_liquid_figure_through_the_model`, `test_a_unit_picked_in_one_view_reaches_every_view_and_survives_a_restart` |

<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->
<!-- not-restated: 8 % -->

## Required invariants

The simulator must always meet the conditions below.

Every quantity stays in its range:

- all volumes are finite and positive
  (`test_every_volume_and_partition_coefficient_is_refused_outside_its_numerical_envelope`,
  and for a volume that is not a number, `test_rejects_invalid_gas_volume`,
  `test_rejects_invalid_venous_volume` and `test_rejects_invalid_tissue_volume`);
- fresh gas flow, alveolar ventilation, cardiac output, and tissue flows are
  finite and nonnegative (`test_rejects_a_value_that_is_negative_or_not_finite`
  for the three controls, and
  `test_a_perfusion_fraction_outside_its_range_is_refused_by_name_and_value`
  for the share of cardiac output that sets each tissue flow);
- partition coefficients are finite and positive
  (`test_every_volume_and_partition_coefficient_is_refused_outside_its_numerical_envelope`
  and `test_rejects_nonfinite_partition_coefficient`);
- tissue flow fractions sum to one within tolerance (`docs/MODEL.md` § "Blood
  flow to the tissue groups", `test_rejects_perfusion_fractions_that_do_not_sum_to_one`);
- stored agent amounts remain finite and nonnegative
  (`test_a_generated_run_keeps_what_must_hold_after_every_action` after every
  action of generated runs, and
  `test_randomised_control_trajectories_keep_every_invariant` after every step
  of runs whose controls move at random moments. Both check each compartment's
  fraction, and a compartment's amount is its capacity times that fraction);
  and
- derived partial-pressure-equivalent fractions remain finite and within 0
  through 1 (`test_a_generated_run_keeps_what_must_hold_after_every_action` and
  `test_randomised_control_trajectories_keep_every_invariant`).

Agent is neither created nor lost inside the model:

- no compartment creates agent spontaneously
  (`test_no_delivered_agent_keeps_every_store_zero`);
- internal transfers remove and add equal amounts
  (`test_the_compartments_neither_create_nor_lose_agent`); and
- equilibrium produces no net internal transfer (§ "Equilibrium test",
  `test_equilibrium_produces_no_net_internal_transfer`).

The controls do only what they say:

- changing a setting does not reset dynamic state
  (`test_parameter_changes_do_not_reset_dynamic_state`);
- Pause stops simulated time from advancing
  (`test_pause_stops_simulated_time_and_the_stored_state`);
- Reset clears dynamic state while preserving settings
  (`test_reset_preserves_settings_and_clears_dynamic_state` for the simulation
  state, and `test_reset_preserves_all_user_settings` for the Reset a learner
  presses); and
- a delivered concentration above the agent's vaporizer maximum is refused, not
  capped (`test_a_run_cannot_open_or_change_under_a_dial_above_the_vaporizer_maximum`).

A zero flow stops the transfer that it carries:

- zero fresh gas flow prevents new external delivery
  (`test_a_zero_flow_is_a_zero_rate_and_needs_no_branch`);
- zero ventilation prevents circuit-to-patient ventilatory exchange
  (§ "Zero-ventilation test", `test_zero_ventilation_prevents_patient_delivery`);
- zero cardiac output prevents pulmonary and tissue perfusion
  (§ "Zero-cardiac-output test", `test_zero_cardiac_output_prevents_patient_uptake`); and
- zero tissue flow prevents uptake by that tissue (§ "Zero-tissue-flow test",
  `test_a_zero_tissue_flow_leaves_that_group_alone`).

The time steps keep these conditions:

- identical runs produce identical state and run definition, element for
  element, however the steps were grouped in real time
  (`test_identical_runs_produce_identical_snapshots` and
  `test_a_run_reaches_the_same_definition_however_the_ticks_fell`);
- simulated time in seconds is the number of completed steps, because every step is
  one second long (`SIMULATION_STEP_S`,
  `test_elapsed_time_is_the_count_of_steps_in_whole_seconds`);
- a caller cannot ask for a step of another length, and a step that would take
  a run past the supported run length is refused
  (`test_a_run_cannot_be_asked_for_a_step_of_another_length` and
  `test_the_step_past_the_supported_run_length_is_refused`); and
- a step that cannot be completed leaves simulated time and dynamic state
  exactly as the last completed step left them
  (`test_a_failed_step_leaves_every_dynamic_value_bit_identical`).

## Required tests

Each subsection below states one requirement, followed by the test that checks
it.

Every required test except § "Published wash-in and elimination validation test" is
**verification**. Each one asks whether the
implementation solves the intended equations correctly. It checks this by
comparing the implementation against an analytic solution, an independent
integration of these same equations, a conservation identity, or the
implementation's own behavior when a run is divided into steps differently or run at
another setting. None of these
tests asks whether the equations describe the phenomenon. A model can be
numerically flawless and physiologically wrong. A suite made only of these tests
would report the first property as though it had settled the second.

### Preserved circuit reference tests

With no patient ventilation, tests check that the simulated circuit washes in and out as

$$
F_I(t) = F_D+\left[F_I(0)-F_D\right]e^{-t/\tau_C}
$$

where

$$
\tau_C =
\frac{V_C}{\dot V_F}
$$

in compatible time and flow units.

The analytic wash-in and washout tests from v0.0.2 must stay unchanged and
keep passing. In `tests/reference/test_circuit_wash_in.py`, one of the two wash-in tests checks
that the circuit's wash-in matches the equation above (`test_circuit_matches_analytic_wash_in`).
The other checks that wash-in is monotonic and never overshoots
(`test_wash_in_is_monotonic_and_never_overshoots`). In `tests/unit/test_circuit.py`, the washout
test checks that the circuit washes out when the delivered concentration is zero
(`test_zero_delivered_concentration_washes_out_circuit`).

### Zero-agent test

If the model starts with no agent and none is delivered ($`F_D=0`$), every
stored amount and concentration must remain zero.

A test in `tests/reference/test_sevo_patient.py` enforces
this requirement (`test_no_delivered_agent_keeps_every_store_zero`).

### Zero-ventilation test

If $`\dot V_A=0`$, the circuit may wash in, but the patient compartments must receive no new agent through ventilation.

A test checks the zero-ventilation case
(`test_zero_ventilation_prevents_patient_delivery` in
`tests/reference/test_sevo_patient.py`).

### Zero-cardiac-output test

If $`Q=0`$, alveolar gas may change through ventilation, but arterial blood, venous blood, and tissue stores must not change through perfusion.

A test enforces this requirement
(`test_zero_cardiac_output_prevents_patient_uptake` in `tests/reference/test_sevo_patient.py`).

### Zero-tissue-flow test

For any tissue $`i`$, $`Q_i=0`$ must imply $`\frac{dM_i}{dt}=0`$. Two tests
check this.

One test checks the coupled system's matrix
(`test_a_zero_tissue_flow_leaves_that_group_alone` in
`tests/unit/test_governing_equations.py`). The other checks that a tissue's
state stays unchanged at zero flow (`test_zero_flow_preserves_tissue_state` in
`tests/unit/test_tissue.py`).

### Equilibrium test

If all connected compartments have the same partial-pressure-equivalent
fraction, with $`F_I=F_A=F_a=F_v`$ and every tissue group at the same value,
then all internal transfer rates must be zero. A test checks this for
sevoflurane, isoflurane and desflurane.

The test is
`test_equilibrium_produces_no_net_internal_transfer`, in
`tests/reference/test_sevo_patient.py` for sevoflurane and in
`tests/reference/test_multi_agent.py` for isoflurane and desflurane.

### Directional ventilation test

When all else is equal, more alveolar ventilation must make $`F_A`$ approach
$`F_I`$ faster. A test runs the default sevoflurane wash-in at 2 and 8 L/min of
alveolar ventilation, and requires $`F_A/F_I`$ to be higher at 8 L/min at every
whole second of the first minute. In these runs, $`F_I`$ rises more slowly at
the higher ventilation, because the circle system recirculates exhaled gas and
more ventilation carries more agent into the patient.

The test is
`test_higher_ventilation_closes_the_alveolar_to_inspired_gap_faster` in
`tests/reference/test_sevo_patient.py`. It compares $`F_A/F_I`$ because $`F_A`$
alone shows the approach to $`F_I`$ only when $`F_I`$ is the same in both runs.

### Directional solubility test

In controlled synthetic cases, raising $`\lambda_{b:g}`$ must increase blood capacity and slow the rise of $`F_A/F_I`$.

The test is
`test_higher_blood_gas_solubility_slows_alveolar_to_circuit_rise` in
`tests/reference/test_sevo_patient.py`.

### Directional tissue-capacity test

With the tissue's blood flow $`Q_i`$ unchanged, the tissue time constant $`\tau_i`$ must lengthen when the tissue is larger ($`V_i`$) or the agent is more soluble in it
($`\lambda_{i:b}`$):

$$
\tau_i =
\frac{V_i\lambda_{i:b}}{Q_i}
$$

The test is
`test_a_larger_or_more_soluble_tissue_has_a_longer_time_constant` in
`tests/unit/test_tissue.py`.

### Washout test

After loading the compartments, setting $`F_D=0`$ must produce a finite,
nonnegative washout in which the total mass of agent in the system never rises.
Individual tissue concentrations may rise for a time through redistribution.

The washout test therefore must not require every
compartment to decrease monotonically. It is
`test_washout_never_increases_total_system_mass` in
`tests/reference/test_sevo_patient.py`.

### Step-refinement test

**Taking a run in steps changes the model's results only by computer rounding.** The
simulation advances in steps of one second, and the model solves its equations exactly
over each step. So a run taken in steps must agree, to within rounding, with one exact
calculation over the same interval.

Two tests enforce this requirement:

1. One test draws runs of many settings and actions, and after each action compares the
   state with the exact solution of the equations over the action, worked out to 50 digits.
   Each comparison allows the summed rounding bound of the steps taken (§ "How far a
   computed value can be from the exact one"). It is
   `test_a_generated_run_keeps_what_must_hold_after_every_action` in
   `tests/unit/test_generated_runs.py`.
2. The independent solution takes 80 steps in each of the model's steps, and the two
   agree to within rounding (§ "Independent-solution test" below).

Passing these tests shows only that dividing a run into steps does not change the
solution of the model's equations. It does not show that the model
matches a patient. A model with a wrong transfer rate would pass, because it
gives the same result however the run is divided. A separate test checks that the equations
are solved correctly (§ "Independent-solution test" below). Another compares
the model with patient measurements (§ "Published wash-in and elimination
validation test").

Until 2026-11-21 a run could take a step from 1 ms to 0.1 s, and two tests compared
60 s sevoflurane runs at different steps. The first compared the alveolar, vessel-rich
and mixed-venous concentrations at steps of 0.1 s, 0.05 s and 0.025 s. A gap is the
absolute difference between two compared runs in one concentration, expressed as a
fraction. The worst gap between successive halvings was 3.4e-16 (from a run on
2026-11-01). The second compared the 0.1 s step with the 1 ms step, and its worst gap
was 2.4e-15 (from a run on 2026-10-03). Both tests were removed when a run kept one
length of step.
<!-- not-restated: 1 ms -->

A method that does not solve the equations exactly fails a limit at the level of
rounding error, because its result moves with the step. Euler's method, for example,
gave gaps of up to 7.1e-7 in those three concentrations at the first test's steps, and
1.7e-6 in the circuit (from a run on 2026-11-21). To test such
a method, check that each halving of the step shrinks every gap by a predicted
factor. The factor is about two when the error is proportional to the step, as
Euler's is. The model's own gaps did not shrink with the step.

### Independent-solution test

The model's solution for its six coupled concentrations must be checked against
an independently written solution of the same equations that shares no solving
code with the model. The independent solution may load the parameter files and
nothing else from the simulator's code, because a comparison with code derived
from the model would check the model against itself and verify nothing. Tests
enforce that restriction.

The comparison covers every shipped agent, and its limit is
**absolute**:

$$
\max_k \left| F_k^{\mathrm{shipped}} - F_k^{\mathrm{reference}} \right|
\leq
4\times10^{-13}
$$

over each of the six concentrations $`k`$ and every run below. *Shipped* marks the
model's result and *reference* the independent solution's. Concentrations here are
fractions. The comparison takes each run's largest difference over its whole length,
because that difference falls at no predictable moment.

**Runs held at the reference point for as long as one hour may differ from the
independent solution by up to $`10^{-12}`$.** The reference point is 5% delivered,
4 L/min fresh gas, and the reference adult's default alveolar ventilation and cardiac
output. A test holds each agent there for 60, 600 and 3600 s,
and compares each result with the independent solution at that time. The
limit for these runs is looser than the one above because the one-hour run builds up
more rounding than any run below.
<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->
<!-- not-restated: 5 % -->

**The only difference between the two solutions is computer rounding.** The model
solves its equations exactly over each step, so in exact arithmetic the two solutions
would be identical. Rounding
builds up with the *number* of steps rather than with their length, so a longer run
differs by more.

Within one step, the model never updates a compartment from a value that the same
step has already changed. So it leaves no error that runs in one direction, and the
difference between two compartments' concentrations is as accurate as each
concentration.

**The $`4\times10^{-13}`$ limit leaves room for rounding that differs between
computers, but not for the error of an approximate method.** It is a chosen limit,
not the bound on a run's rounding that `core/rounding.py` derives. That bound, for the
runs at the corner of the supported settings, is larger than the loss of exactness
that the test must catch, so a limit set at it would pass that loss. Two
conditions set the chosen limit instead:

1. It must fail the model's result with every concentration made 1e-11 too large, in
   proportion. At the highest desflurane dial setting that moves a concentration by
   $`1.8\times10^{-12}`$, four and a half times the limit.
2. It must pass the rounding that differs between computers. The limit was set
   when a run could take a step of 0.1, 0.05 or 0.025 s. Solving the five runs below
   at those three steps moved the model's result by more than its difference from
   the independent solution, and the limit was set above that spread. A run now
   takes one length of step, so the spread cannot be measured again. It still covers
   a one-second run. The derived bound grows with the number of steps and doubles
   with each squaring that a step's calculation needs. A one-second step of these
   runs needs two or three squarings and a 0.1 s step needed none, so each run's
   bound in one-second steps is at most 0.8 times its bound in 0.1 s steps.
<!-- not-restated: 0.05 -->

Even the largest
difference found is nine orders of magnitude smaller than the worst error of the
earlier method, which solved the equations only approximately. The limit is still
nearly nine orders of magnitude below the error of any method that does not solve
the equations exactly, so the test fails as soon as such an error returns.

**The earlier method was an operator split, which the exact step replaced in v0.4.4,
released on 2026-09-06** (`PL-GS5X`). Within each step it solved the model's
exchanges one at a time and in a fixed order, each exactly, while it held every other
flow still. Because the exchanges were solved one after another rather than together,
the step as a whole was not exact, even though each exchange was solved exactly. The
error it added over a fixed span of simulated time was proportional to the step's length. § "Selected method (as implemented)" describes the exact step.

#### The runs the test covers

The comparison covers *trajectories*, runs whose settings change over time, as well as
runs at fixed settings. A run of the application is a sequence of settings, each held
until someone moves a slider. A slider move puts an approximate method under the most
strain, because the concentrations are then far from where the new settings will
settle them, and the method's error grows with how fast they change. Runs whose
settings never change are the smaller part of what the interface produces. If the
test that every release must pass covered only those, it would claim more
checking than its evidence supports. The test therefore drives five kinds of run:

- *ordinary use*, held for 600 s: each agent's own 1 MAC delivered, 4 L/min
  fresh gas, and the reference adult's default alveolar ventilation and cardiac
  output. The last three runs below were chosen where the earlier method's error
  was largest. This run is chosen for ordinary clinical settings, so that a claim
  about what the interface displays is not established only at its extremes.
- the *reference point* described above, held for up to one hour.
- the *envelope corner*, held for 600 s: each agent's highest delivered
  concentration (`max_delivered_concentration_percent`), with fresh gas flow,
  alveolar ventilation and cardiac output at their highest supported values,
  10, 12 and 10 L/min. These are also the sliders' maxima.
- a *ventilator start*: the envelope corner, but with alveolar ventilation at
  zero for the first 300 s and then at its maximum. While ventilation is off, the
  circuit fills to the dial setting and the lungs take up none of it. This is an
  ordinary manoeuvre, and the earlier method exceeded the limit set from runs
  held at the corner.
- an *unperfused load, then dial off*: the envelope corner with cardiac output at
  zero for 600 s, then perfusion at its maximum with the vaporizer closed for
  300 s. During the first 600 s the circuit and alveoli saturate while every
  blood and tissue compartment stays empty, which sets up the widest spread of
  concentrations that the sliders allow. It is the only trajectory that takes
  cardiac output or the delivered concentration to its minimum. Under the
  earlier method it had the largest error of any trajectory, which is why it was
  added. Under the present method its difference is smaller than the envelope
  corner's and the ventilator start's.

<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->

**Random runs cover combinations of settings that nobody listed.** The five runs
above change their settings once or never. A learner moves four sliders again and
again, in combinations that nobody listed. So the test also drives three random runs
for each agent. Each lasts 600 s and moves the controls every 1 to 20 s, sometimes
to the very end of a slider's range, so zero ventilation, zero perfusion and zero
fresh gas flow are all reached. These runs must meet the same $`4\times10^{-13}`$
limit as the five above, and they stay below the worst of them.

#### Checks at every step of the random runs

A second test drives the same random runs through the full simulation. It checks
that every step runs without error and is counted, and that the agent accounting
adds up after each one. It also checks that each of the six concentrations stays
finite, at or above zero, and at or below the highest concentration delivered so
far. No compartment can hold agent at a higher concentration than was ever
delivered, because each is fed only from the others and from the vaporizer.

#### The tests and the figures behind the comparison

The comparison is in `tests/reference/test_coupled_dynamics.py`,
where the independent solution is called the oracle. The five runs are compared by
`test_exact_step_matches_the_independent_solution_everywhere`, and the random runs by
`test_exact_step_matches_the_independent_solution_on_randomised_trajectories`. The two tests that enforce the
restriction check what the oracle imports and what its functions call
(`test_oracle_imports_no_solver_from_core`,
`test_oracle_bodies_call_no_solver_from_core`). Each figure in this subsection is an
absolute difference in fraction, taken as the largest over the whole run.

- **Why the limit is not a multiple of the step.** The earlier method had an
  error proportional to the step, $`C\,\Delta t`$, so a bound on the
  coefficient $`C`$ bounded the error at every step size. The
  present method's error has no such coefficient.
- **What the earlier method's limits measured, and why they were retired**
  (`PL-X9KD`, 2026-09-06). The bound on $`C`$ was 2.8e-3 s⁻¹, 1.22 times the
  worst coefficient measured, 2.29e-3 s⁻¹. Expressed as a coefficient, the exact
  step's worst difference was 7.747e-12 s⁻¹, so the bound was 3.61e8 times
  larger, and the three tests that used it passed with 8.6 to 9.7 orders of
  magnitude to spare. The fourth test checked that the error halved with the
  step: each ratio of the error at one step to the error at half that step had to
  lie between 1.9 and 2.1. It returned early, asserting nothing, wherever the
  error was below a floor of 1e-12, and it did so on all nine of its cases.
  Without the early return all nine would have failed, because the ratios ran
  from 0.147 to 18.6. On desflurane's ventilator start the floor was only 1.29
  times the measured error, so a computer that rounded slightly differently
  would have failed correct code. That test took about 25 s of the file's 56 s.
  The test that replaced the first three had a limit of 5e-12 at the time,
  6.45 times the worst difference. The retired comparison over 3600 s found
  the difference at that horizon two to sixteen times its 600 s value, largest
  at the end of the run and in muscle.
<!-- not-restated: 2.1 -->
- **Why the difference is rounding.** The independent solution takes 80 steps of
  0.0125 s in each of the model's steps, short enough that error from its own
  method no longer adds to the difference. A test checks that the 80 steps cover
  one second exactly
  (`test_the_oracle_takes_a_whole_number_of_steps_in_each_shipped_step`). When
  the model's step was 0.1 s, shortening the independent solution's steps
  eightfold again, to 0.0015625 s, moved the largest differences by at most 11%,
  some up and some
  down. A difference that still held error from the independent solution's own
  method would fall about four-thousandfold and never rise, so a difference that
  moves a few percent either way comes from rounding in the two solutions.
- **Why the independent solution steps at 0.0125 s** (`PL-B1WW`, 2026-09-07,
  when the model's step was 0.1 s). At its earlier step of 0.05 s the
  independent solution had converged only at the reference point held. The
  worst difference reported then was 7.7470e-13, for desflurane on the
  ventilator start, alveolar, at 307.4 s. Against an independent solution at
  0.0015625 s, the independent solution's own error made up 7.7562e-13 of it,
  99.88%, and the model's own error 9.1593e-16. Across the runs that set the
  limit, the independent solution's share ran from 86% to 99.8%. At steps of
  0.05, 0.025, 0.0125 and 0.00625 s, that run's largest difference was
  7.7377e-13, 4.7351e-14, 1.3906e-14 and 1.2490e-14. It stops falling at
  0.0125 s. At 0.025 s the independent solution still contributed about two
  thirds of the figure.
<!-- not-restated: 0.05 -->
  - The finer step took this test file from 39.5 s to 79.2 s run serially, and
    the whole suite as CI runs it from 43.0 s to 55.5 s. The suite figures are
    the means of two paired runs on a 4-CPU container at `-n 8`, with the cold
    first runs discarded.
  - Richardson extrapolation, which combines steps of $`h/2`$ and $`h/4`$ as
    $`(16y_{\text{fine}} - y_{\text{coarse}})/15`$, costs three times the 0.05 s
    solution against four times for this step. It reached the same lowest
    difference, 1.6029e-14 against 1.5786e-14. It was rejected because it adds
    a mechanism to the one part of the test that a reviewer must be able to
    check line by line against a textbook.
- **Rounding builds up with the number of steps.** Before the step was fixed at
  one second (`PL-SZ6G`, 2026-11-21), sevoflurane held at the reference point
  for 600 s differed from the independent solution by 2.8935e-15 at a step of
  0.1 s, 1.3385e-14 at 0.05 s and 3.8337e-14 at 0.025 s: more steps, more
  rounding.
- **The limit's margin for rounding on other computers.** The earlier method's
  limit carried a margin of 1.22. Its error coefficient came out the same on
  every computer, but rounding does not. A different `exp` implementation or a
  fused multiply-add instruction moves the last bits of both solutions. The
  spread between steps of 0.1 s, 0.05 s and 0.025 s, found without the independent
  solution, reached 1.07e-13. The limit is 3.7 times that spread and 6.8 times
  the largest difference at those steps, 5.89e-14. It is 28 times the largest
  difference at the one-second step, 1.43e-14. That wider margin is not a reason
  to tighten the limit, because the limit is set by the spread and not by the
  difference. The spread still covers a one-second run by `run_rounding` in
  `core/rounding.py`, which counts steps times $`2^{s}`$ for $`s`$ squarings. At the
  envelope corner a one-second run takes 600 steps of three squarings, 4 800 by that
  count, against 6 000 steps of none at 0.1 s (squarings counted 2026-11-22).
- **The loss of exactness the limit must catch.** Making every concentration
  of the model's result 1e-11 too large, in proportion, raises the largest difference
  on the five runs to 1.81e-12 at the one-second step, and the limit fails it
  (simulated 2026-11-22). The derived bound from `run_rounding` is $`1.1\times10^{-11}`$
  to $`1.6\times10^{-11}`$ of a concentration's size on the three runs at the envelope
  corner, so a limit set at that bound would pass this loss.
- **Results for the five runs.** At the one-second step, the largest differences
  are 1.43e-14 for the *envelope corner*, 1.16e-14 for the *ventilator start*,
  6.13e-15 for the *unperfused load, then dial off*, 2.49e-15 for the *reference
  point* and 2.07e-15 for *ordinary use* (simulated 2026-11-21). Desflurane
  gives the largest difference of the three agents on every run but the
  reference point, where sevoflurane does.
  The five lie within a factor of 6.9 of each other, because rounding does not
  grow with how far settings move. On the unperfused load, desflurane's largest
  difference falls at 399 s, while the blood and tissue states are still exactly
  zero. Rounding does
  build up over a run. Three desflurane ventilator starts in a row reach
  1.23e-14, against 1.16e-14 for one (simulated 2026-11-21). At the earlier step
  of 0.1 s, the largest of the five was 1.58e-14, for *ordinary use* (simulated
  2026-09-07). The test then repeated all five at 0.05 s and 0.025 s. The largest
  there was **5.89e-14**, for desflurane on a ventilator start at 0.025 s
  (simulated 2026-10-25). The earlier
  method's largest error over these runs was 2.29e-4 at 0.1 s.
- **The pinned reference states.** The test file pins the reference states,
  storing the independent solution's own results at the reference point as fixed
  numbers. Re-pinning them from the model would turn this test into a
  self-comparison. A change to the independent solution or to a parameter file
  must be re-derived and reviewed rather than silently adopted.
- **Runs held to one hour.** The test of these runs
  (`test_the_shipped_step_reaches_the_pinned_reference_horizons`) takes its limit,
  an absolute $`10^{-12}`$, from a named constant (`HELD_RUN_ROUNDING_BOUND`). A
  separate test ties the independent solution to the pinned reference states. The
  one-hour run takes 3 600 steps and reaches **1.58e-14**, for isoflurane in muscle
  (simulated 2026-11-21). The 600 s figures are at most 2.35e-15, and the
  60 s figures at most 5.34e-16. The limit is 63 times the largest figure. It was
  set at the earlier step of 0.1 s, when the one-hour run reached 7.16e-14 and
  dividing the hour into steps of 0.1 s, 0.05 s and 0.025 s moved the
  model's result by up to 2.17e-13. The limit is 4.6 times that spread. The
  spread still covers the hour in one-second steps, which takes two squarings a
  step: 3 600 steps count 14 400 by `run_rounding`'s count, against 36 000 steps
  of none at 0.1 s (squarings counted 2026-11-22). This limit catches a coarser
  loss of exactness than the five runs' limit. These runs hold the dial at 5%, so
  making every concentration 1e-11 too large, in proportion, moves the largest
  difference to only 4.67e-13, which passes. At 2.2e-11 it reaches 1.02e-12, which
  fails (simulated 2026-11-22). The five runs' limit catches the smaller loss.
<!-- not-restated: 5 % -->
- **When the largest difference falls.** With the earlier method it fell soon
  after a change: about 85 s into a wash-in at fixed settings, and about 13 s
  after a setting change. With the present method it falls wherever rounding
  peaks. In runs on 2026-11-21:
  - Four of the fifteen pairs of agent and run peak in the run's last two
    seconds. At the envelope corner, isoflurane and desflurane peak at 600 s and
    sevoflurane at 442 s.
  - On the ventilator start, sevoflurane and isoflurane peak in the circuit while
    ventilation is still off, at 264 s and 233 s. Desflurane peaks in the run's
    last two seconds.
  - On the unperfused load, isoflurane and desflurane peak during the loading
    phase, long after the circuit and alveoli have saturated. Sevoflurane peaks
    19 s after that phase.
  - On none of the five runs is muscle the compartment with the largest
    difference. Muscle has it only at the end of the one-hour runs.

  When a run could take other steps, the peak moved with the step. In runs on
  2026-10-25:
  - At the 0.1 s step, nine of the fifteen pairs peaked in the last 1.5 s of a
    600 s run. Only sevoflurane on the ventilator start peaked soon after a
    setting change, 6.4 s after ventilation started.
  - At 0.05 s, four of the fifteen pairs peaked in the last 1.5 s, and at
    0.025 s five did. The ventilator start peaked in the circuit between 236 s and
    283 s, while ventilation was off, for every agent at 0.025 s and for two of
    the three at 0.05 s. The largest difference in any run was one of these peaks,
    at 236.1 s.
  - At each of the three steps, the unperfused load peaked during its loading
    phase, between 350.8 s and the phase's end at 600 s.

  So the runs contain the moments at which the earlier method's error peaked,
  and that kind of error is what the test exists to catch. They do not contain
  the largest rounding difference, which was still reaching
  new highs in the last two seconds on those four pairs. The pinned reference states
  follow that growth at held settings out to 3600 s.
- **How the envelope corner and the two runs that change settings were chosen.**
  A sweep computed the earlier method's error coefficient:
  - When one setting at a time was varied in runs at fixed settings, the error
    rose steadily with fresh gas flow and alveolar ventilation, up to their
    slider maxima. Against cardiac output it was lowest near 5 L/min and rose
    toward both ends, more toward the top. The equations are linear in the
    delivered fraction, so each agent's worst dial setting was its vaporizer
    maximum.
  - For runs that change settings, the sweep first tried every combination of
    extreme settings in both phases, then varied each setting around the worst
    combination. The worst point was always the first setting change after the
    loading phase filled. Repeating the cycle three or six times did not raise
    the peak, so the earlier method's error did not build up over a run. A third
    phase between the two never raised the error.
  - Along every setting except cardiac output during loading, the error rose
    steadily toward the corner used. That setting was worst at *zero*, the
    opposite end from the held-settings corner.

  With the earlier method, the unperfused load had the larger error and the
  ventilator start the smaller. With the present method the two have swapped
  places, and rounding builds up over a run. So the sweep still shows where an
  approximate method has its largest error, which is the error the test exists
  to catch. It does not bound the present method's rounding, which a longer run
  raises. The steady rise along each setting was observed in the sweep, not
  proved, and a change to the equations could move the worst case off these
  runs. So repeat the sweep after such a change.
- **The random runs.** Each is fixed by a seed, so that a failure can be repeated
  exactly. Each starts with every compartment empty, at random settings within the
  supported ranges. Controls move only on a step boundary. At each move, each
  control changes with probability one half, at least one always changes, and
  one move in five lands exactly on the end of a slider's range. The largest
  difference in any random run is 4.02e-15, for desflurane in the circuit
  fraction (simulated 2026-11-21). A run that changes its
  settings 48 to 53 times takes as many steps as one that never does, so it builds
  up as much rounding and no more. The second test
  (`test_randomised_control_trajectories_keep_every_invariant`) runs the full
  simulation (`SimulationState`). Its upper limit on each concentration replaces
  a limit of 1. A looser upper limit would let a model change drive a compartment
  to several times the dial setting. The limit allows each concentration to
  exceed the highest delivered so far by 1e-14 of it, for rounding. That is a
  chosen allowance, about a thousand times tighter than the bound on rounding
  that `core/rounding.py` derives for these runs. It holds because no compartment
  comes near the limit: the highest reached 68% of the highest concentration
  delivered (simulated 2026-11-22).
- The test file restates the supported ranges above and checks them against the
  ranges the model declares (`core/supported_ranges.py`), so widening the declared
  ranges cannot silently leave this test covering only part of them.
<!-- not-restated: 5 L/min -->

### Published wash-in and elimination validation test

This test is the **validation** half, and the only required test whose expected values
come from published measurements. § "Independent-solution test" above answers a different
question. A pass of one says nothing about the other.

**This section covers two comparisons, in opposite directions.** The first is
$`F_A/F_I`$ at 30 minutes of **wash-in**, which agrees with the published
measurements. The second is $`F_A/F_{A0}`$ at 5 minutes of **elimination**,
which does not agree. Both come from the same volunteers in the same sitting.
§ "The early wash-in curve against the published figures" below extends the
wash-in comparison to the first 25 minutes.

$`F_A/F_I`$ at 30 minutes of wash-in is the classic measured quantity in the
uptake literature. Yasuda et al. published it for all three shipped agents in
two volunteer studies:

| Agent | $`F_A/F_I`$ at 30 min | Cohort | Published $`F_I`$ | Source |
| --- | --- | --- | --- | --- |
| Sevoflurane | 0.850 ± 0.018 | n=7 | 1.0% | Anesth Analg 1991;72:316-24 |
| Isoflurane | 0.733 ± 0.027 | n=7 | 0.6% | Anesth Analg 1991;72:316-24 |
| Desflurane | 0.90 ± 0.01 | n=8 | 2.0% | Anesthesiology 1991;74:489-98 |
| Isoflurane | 0.73 ± 0.03 | n=8 | 0.4% | Anesthesiology 1991;74:489-98 |


The full citations of both papers, with a record of what was read in each, are
in the reference list, `docs/references/README.md`
§ "Yasuda et al. 1991 — the two human kinetics papers".

Both papers report a second measured quantity on the same subjects, in the
opposite direction. That quantity is $`F_A/F_{A0}`$ after five minutes of
elimination, which begins where the 30-minute administration above ends.
$`F_{A0}`$ follows each paper's own definition: the last alveolar fraction
recorded during that administration. So the two comparisons form one
continuous protocol rather than two separate ones.

| Agent | $`F_A/F_{A0}`$ at 5 min | Cohort | Source |
| --- | --- | --- | --- |
| Sevoflurane | 0.157 ± 0.020 | n=7 | Anesth Analg 1991;72:316-24 |
| Isoflurane | 0.223 ± 0.024 | n=7 | Anesth Analg 1991;72:316-24 |
| Desflurane | 0.14 ± 0.02 | n=8 | Anesthesiology 1991;74:489-98 |
| Isoflurane | 0.22 ± 0.02 | n=8 | Anesthesiology 1991;74:489-98 |

All eight figures in the two tables are mean ± SD. They were read from the two
abstracts and checked against PubMed on 2026-09-06.

**For wash-in**, the model must land inside the published standard deviation
for every row. It must also reproduce the ordering by solubility that the two
studies were run to test. That is, $`F_A/F_I`$ is higher for desflurane than
for sevoflurane, and higher for sevoflurane than for isoflurane. The ordering
is required because each row could pass its own tolerance while the agents sat
in the wrong order. The model meets both requirements. The elimination rows
have a different requirement, described below, because the model does not land
inside their spread.

**The tolerance is the published spread, and the operating point is not
fitted.** The test reads alveolar ventilation and cardiac output from
`reference_adult.json` at run time rather than writing them into the test. The
test fails if those defaults stop being 4.0 and 5.0 L/min. The whole
comparison rests on this assertion, because the agreement is sensitive to both
flows. A change of 1 L/min of alveolar ventilation either way puts all three
agents outside their published spread. A change of 1 L/min of cardiac output
moves every agent by more than one published standard deviation. An operating
point chosen to make the comparison pass would therefore make the result
circular. The operating point is instead the shipped default. It is cited to
the Gas Man workbook under `docs/PARAMETERS.md` § "Parameter provenance", and it was fixed in
v0.1.0 before any comparison to Yasuda existed.
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5 -->

Fresh gas flow is the one setting that the test chooses. It is 10 L/min, so that $`F_I`$ has
settled by 30 minutes instead of still rising. Here $`F_I`$ is the modeled *circuit* fraction,
not the vaporizer dial. A settled $`F_I`$ matches the protocols, which held an inspired
concentration at the airway. This choice does not decide the wash-in result. The test shows
every agent inside its published spread at every fresh gas flow from 1 to 10 L/min. The choice
does decide almost all of the elimination result, so the two comparisons are not equally strong.
The papers published four different $`F_I`$ values, and the test compares all four against one
delivered fraction. That is valid because the governing equations are linear in that fraction.
The test checks this for both ratios across the published range.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

**The elimination comparison does not agree.** At the default settings, and at the same
10 L/min that the wash-in comparison uses, the model has more alveolar agent at five minutes
than every cohort did. These values come from simulator runs on 2026-09-07:
<!-- not-restated: 10 L/min -->

| Agent | Cohort | Model | Published | Distance |
| --- | --- | --- | --- | --- |
| Sevoflurane | n=7 | 0.2328 | 0.157 ± 0.020 | +3.79 SD |
| Isoflurane | n=7 | 0.3227 | 0.223 ± 0.024 | +4.15 SD |
| Desflurane | n=8 | 0.1626 | 0.14 ± 0.02 | +1.13 SD |
| Isoflurane | n=8 | 0.3227 | 0.22 ± 0.02 | +5.13 SD |

So the check on these values is a **regression** pin. It holds the model's own ratio fixed, so
that any change to washout fails the test and has to be explained. It claims nothing about
agreement. The test does make three claims about elimination, and the model meets all three.
They are the published ordering by solubility (desflurane leaves fastest, then sevoflurane,
then isoflurane), independence from the delivered fraction, and the sign of the departure.

**Most of that departure comes from the breathing system, not from the tissue
return**, because of how the two ratios are defined. $`F_A/F_I`$ has the inspired fraction in
its denominator, so whatever a breathing system does to $`F_I`$ divides out. That is why the
wash-in comparison is inside the published spread at every supported flow. $`F_A/F_{A0}`$ has
no such term. It is the alveolar fraction divided by its own value five minutes earlier. So
agent that returns to the alveoli *from the circuit* counts exactly as though it had come out
of the patient. This model always rebreathes. Its one circuit (`docs/MODEL.md` § "What the model represents")
recirculates gas, apart from the fresh gas that enters and the gas that leaves through the
exhaust. The inspired gas *is* circuit gas. So during an elimination $`F_I`$ settles near
$`\dot V_A/(\dot V_A + \dot V_F)`$ of $`F_A`$, where $`\dot V_F`$ is the fresh gas flow. That
is 0.29 at the highest supported flow, and the simulated value at five minutes was 0.30 to 0.32.
The published protocols did not rebreathe. Each study gave the agents through a
non-rebreathing circuit. At exactly 30 minutes, each exchanged it for a fresh inspiratory and
expiratory circuit (*Anesth Analg* page 317, *Anesthesiology* page 490). Neither paper states
the inspired fraction during elimination, so an inspired fraction at or near zero is inferred,
not reported. This model cannot be set to that fraction at any supported flow.

**The open-circuit diagnostic, and why its numbers are not this simulator's.** A test can run
the same five minutes with the rebreathing taken away. When the vaporizer is closed, the test
empties the circuit and enlarges it to 10 000 L, the largest volume that the model accepts.
After each step of the elimination, it
discards whatever the patient exhaled into the circuit and records it as exhausted agent.
Collecting the whole expirate has the same effect. This keeps $`F_I`$ near zero. The circuit is
enlarged because the test can empty it only once a second, and in the shipped circuit one
second of exhaled gas would raise $`F_I`$ to about a hundredth of $`F_A`$. **This condition exists only in the test.
No fresh gas flow, dial position or patient setting of the simulator produces it.** A
non-rebreathing mode was not built, because it would change the model boundary and add one
more mode for the interface to show (project owner, 2026-09-06). Nobody running the
application sees the numbers below, so any restatement of them must carry this warning. The
shipped column comes from simulator runs on 2026-09-07, and the open-circuit column from runs
on 2026-11-21:
<!-- provenance: core/numerical_envelope.py MAXIMUM_VOLUME_L = 10000 -->

| Agent | Cohort | Shipped | Open circuit | Published |
| --- | --- | --- | --- | --- |
| Sevoflurane | n=7 | +3.79 SD | 0.1540, −0.15 SD | 0.157 ± 0.020 |
| Isoflurane | n=7 | +4.15 SD | 0.2387, +0.65 SD | 0.223 ± 0.024 |
| Desflurane | n=8 | +1.13 SD | 0.0934, −2.33 SD | 0.14 ± 0.02 |
| Isoflurane | n=8 | +5.13 SD | 0.2387, +0.93 SD | 0.22 ± 0.02 |
<!-- not-restated: 0.65 -->

**Three of the four cohorts land inside the published spread once the rebreathing circuit is
removed, and desflurane misses on the other side.** For sevoflurane, and for isoflurane in
both cohorts, the rebreathing circuit accounts for the whole of a gap 3.8 to 5.1 published
standard deviations wide. So this model's vessel-rich return does reproduce a human
elimination once the breathing systems are matched. For desflurane, removing the circuit more
than closes the gap. The model crosses its published mean and settles 2.33 SD below it, so it
washes out *faster* than the volunteers did. With the circuit gone, that residual is a
disagreement about tissue return. § "Desflurane's residual" below lists the explanations that
were ruled out and what remains. The shift between the two conditions is 3.5 to 4.2 SD per cohort. A test fails
if any cohort's shift is not more than 3.0 SD, so it fails if the circuit stops explaining the gap. Without the
circuit, the elimination does not measurably depend on fresh gas flow. With it, the
elimination moves by 11.5 to 21.6 SD between 1 and 10 L/min.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

Neither condition validates the elimination a user watches, and no test claims
that it does. The elimination this simulator runs is the rebreathing one. What
is asserted about it is the regression pin above.

**A band of one standard deviation tests a plausible individual, not the
cohort mean.** A deterministic model compared against a cohort *mean* would
conventionally be judged against the standard error of that mean (SEM),
$`\text{SD}/\sqrt{n}`$. For these cohorts that band is 2.6 to 2.8 times
narrower. This section makes the weaker claim on purpose. It asks only whether
the model is a **plausible individual** drawn from the published cohort.
Desflurane's wash-in sits at +0.79 SD, which is +2.2 SEM. So it passes this
claim and would fail a claim about the mean. A passing wash-in must not be
restated as "reproduces the published mean", because no test here tests that.

**Four caveats limit how strongly a pass may be stated.** The first two apply
to both directions. The last two apply only to the elimination comparison. All
four belong beside any statement of this result, wherever it is restated.

1. *The published subjects were breathing nitrous oxide.* Both protocols ran
   65–70% N₂O at the same time as the potent agents. So the measured curves
   carry a second-gas effect that this model cannot reproduce.
   `docs/MODEL.md` § "What the model does not represent" excludes nitrous oxide,
   simultaneous gases, and concentration and second-gas effects.
   `docs/MODEL.md` § "Assumptions" states that carrier gases are assumed not to
   affect kinetics. The comparison is therefore not perfectly matched,
   and the mismatch runs in a direction that is not obviously conservative.
2. *These are Gas Man parameters, derived to reproduce Eger's data.* The
   partition coefficients being tested descend from the same lineage as the
   measurements they are tested against (see `docs/PARAMETERS.md` § "Parameter provenance"). A pass
   shows that this implementation reproduces the intent of its parameter set.
   It does not show that the parameter set is independently right. That is
   weaker than "validated against a human measurement", and it must not be
   described as more. The intent itself is least reliable in the wash-in
   direction, which is where this comparison looks. Gas Man's own published
   agreement with patients is materially worse during wash-in than during
   maintenance (see `docs/MODEL.md` § "Gas Man in patients").
3. *The breathing systems differ, and by more than the measurement's own
   spread.* The simulated results above put the difference at 3.5 to 4.2
   published standard deviations per cohort. Any statement that this model
   eliminates more slowly than these volunteers did has to carry this caveat,
   because most of that difference comes from a rebreathing circuit rather than from a
   patient.
4. *This model has no metabolism, and it has no counterpart to the fourth
   compartment that human washout needs. Neither omission matters over five
   minutes.* Over five minutes of elimination, metabolism is negligible for all three agents,
   and the papers bound it. They report recovery, the agent recovered during elimination
   divided by the agent taken up. Recovery was 101 ± 7% for sevoflurane and 101 ± 6% for
   isoflurane in the first study, and 105 ± 25% for desflurane and 102 ± 13% for isoflurane in
   the second. Halothane gave 64 ± 9%, so the same method does detect a metabolized agent. The
   papers' elimination curves over several days must not be added to this comparison. Over
   days, the missing metabolism is no longer negligible. Nor is the fat group's blood flow,
   which `docs/MODEL.md` § "The fat group's blood flow" weighs against two human sources that
   disagree about its direction. The measured tail also moves beyond what this model can follow within the 24
   hours for which a run is supported, long before days have passed. Every washout that these
   papers fitted needed a fourth compartment between muscle and fat, which this model lacks. On
   the published mean coefficients, that compartment's term is the largest in the measured
   curve for most of the supported span (`docs/MODEL.md` § "Intertissue diffusion: the missing
   fourth compartment" gives the hours). At five minutes, that term is about one part in twenty of what remains. A comparison over those
   hours would show an omission rather than a parameter. So the gap over those hours is
   computed beside this comparison and is not part of it. § "The first 24 hours of elimination
   against the published mean curves" records its size and direction hour by hour, and claims
   no agreement.

<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The test is `tests/reference/test_published_wash_in_and_elimination.py`.
It checks the five-minute elimination ratio against a stored value to $`1\times10^{-4}`$ absolute,
and its failure message gives the distance from each published mean. No tolerance is wide enough
to hide the disagreement. Neither paper's full text is in PubMed Central. Both are in the
private reference corpus that `docs/references/README.md` describes, and each has an
extraction note in `docs/references/` that gives the pages cited above. The open-circuit
condition is a test-only driver. Its $`F_I`$ is not zero, because exhaled gas refills the circuit
during each step before being discarded. The remaining $`F_I`$ is at most
$`\dot V_A \Delta t / V_C`$ of $`F_A`$ at the start of the step, or 6.7 × 10⁻⁶ at the shipped
ventilation, the one-second step and the driver's enlarged circuit. The test also checks this residual $`F_I`$ and the model's
mass balance across the discards. Across the supported flow range, the open-circuit elimination
changes by 1.3 × 10⁻¹⁰ published SD at most.
<!-- not-restated: 1.3 -->

#### Desflurane's residual, and why the parameter file was not changed

The obvious explanation for that residual is that desflurane's vessel-rich
coefficient is too low. § "What the published-data gate can and cannot
resolve" has a table of how far each ratio moves when one coefficient is raised
by 10%. It shows that the five-minute ratio depends mostly on
the vessel-rich tissue:gas coefficient and barely on the blood:gas coefficient. A tissue group with too
little capacity empties too fast. That explanation fits the arithmetic, but the
measured tissue solubility rules it out, as the next paragraphs show.

**Raising the coefficient does close the gap, and it costs almost nothing in
the wash-in row.** Desflurane's stored vessel-rich tissue:gas coefficient is
0.54, and its blood:gas coefficient is 0.42. Together they imply a
tissue:blood ratio of 1.286. The table below instead solves for the
coefficient that reproduces each cohort's published five-minute ratio. It does
so at the shipped operating point, with the apparatus removed (simulated
2026-09-08):

<!-- provenance: data/agents/desflurane.json tissue_gas_partition_coefficients.vessel_rich = 0.54, blood_gas_partition_coefficient = 0.42 -->
<!-- derived: 1.286 from data/agents/desflurane.json tissue_gas_partition_coefficients.vessel_rich = 0.54, blood_gas_partition_coefficient = 0.42 -->

| Agent | Tissue:blood demanded | Measured human brain:blood | Distance |
| --- | --- | --- | --- |
| Sevoflurane | 1.74 | 1.70 ± 0.09 | +0.4 SD |
| Isoflurane | 1.45 | 1.57 ± 0.10 | −1.2 SD |
| Desflurane | 2.24 | 1.29 ± 0.05 | +19 SD |

<!-- not-restated: 0.05 -->

At a tissue:blood ratio of 2.24, desflurane's elimination lands on the
published 0.140. Its wash-in row stays inside its published spread, at +0.55
SD. That is not luck. The vessel-rich group's time constant is 2.0 to 2.7
minutes across the three agents, so the group is fully equilibrated after a
30-minute administration. Its capacity is therefore nearly invisible in
$`F_A/F_I`$ and shows up almost entirely in the elimination. So the two
published rows do not conflict with each other, and a single coefficient
satisfies both.

**The measured tissue solubility rules the change out.** The
measured column above comes from Yasuda's study of human tissue. The same
group published it three years before its pair of kinetic studies:

- Yasuda N, Targ AG, Eger EI 2nd. *Solubility of I-653, sevoflurane,
  isoflurane, and halothane in human tissues.* Anesth Analg 1989;69(3):370-3.
  PMID 2774233. Brain:blood, mean ± SD: I-653 (desflurane) 1.29 ± 0.05,
  isoflurane 1.57 ± 0.10, sevoflurane 1.70 ± 0.09, halothane 1.94 ± 0.17.
  Read from the abstract and checked against PubMed on 2026-09-08.

<!-- not-restated: 0.05 -->

Two of the three demanded values agree with that measurement. A demanded value is the
coefficient that an agent would need to match its published elimination. Desflurane's
demanded value is nineteen standard deviations above its own measured value, and above the
value that either other agent demands. Adopting it would make desflurane the *most*
tissue-soluble of the three agents, which would invert the ordering that the source paper was
written to report. The stored Gas Man coefficients match that paper's brain:blood values to
within 3%: 1.692 against 1.70, 1.615 against 1.57, and 1.286 against 1.29. So there is no
better value to move to. A test checks that at any vessel-rich coefficient the published human
tissue data support, desflurane's elimination still misses on the same side.

| Coefficient given | $`F_A/F_{A0}`$ at 5 min | Against 0.14 ± 0.02 |
| --- | --- | --- |
| 1.286, shipped | 0.0934 | −2.33 SD |
| 1.39, its own measured mean + 2 SD | 0.0997 | −2.01 SD |
| 1.70, sevoflurane's, the highest of the three | 0.1166 | −1.17 SD |

**Nine other candidates were simulated or struck, and each fails in one of two ways.** Either
it moves sevoflurane and isoflurane as much as desflurane or more, which the published rows
have no room for, or it moves desflurane the wrong way. Rows one to six were simulated on
2026-09-08, and the seventh on 2026-09-13, using the published apparatus's real volume from
the methods sections. Rows one to three and the seventh were simulated again on 2026-11-21,
with the open-circuit test as it is described above. Rows four to six were computed by a separate calculation of the same
equations, which agrees with the simulator to within 0.8%. The eighth and ninth rows were not
simulated. Each is struck because a primary measurement on file rules it out, as described
below the table.

| Candidate | What reaching 0.140 takes | What it costs the other rows |
| --- | --- | --- |
| Blood:gas too low, with each tissue:blood ratio held | ×1.64, to 0.687 | 11.0 SD above Eger 1987's measured 0.424 ± 0.024, and the wash-in row falls to −4.36 SD |
| Alveolar ventilation too high | between 2.5 and 3.0 L/min | at 3.0, sevoflurane +2.1 and isoflurane +2.7 SD, and all three wash-in rows at −2.0 SD |
| Cardiac output | out of reach | 3 to 7 L/min moves desflurane only from −2.6 to −2.1 SD |
| Fast capacity this model omits: lung tissue, pulmonary and arterial blood | about 3 L of blood-equivalent | moves all three agents together (below) |
| A non-ideal lung — shunt or ventilation-perfusion dispersion, both excluded by $`F_a \equiv F_A`$ | moves the wrong way | a 20% shunt takes desflurane from −2.29 to −2.66 SD; a log-normal V/Q distribution at log SD 1.0 takes it to −2.91 |
| Circuit-style rebreathing in the published apparatus, at an assumed ratio | $`F_I/F_A`$ = 0.30 | sevoflurane +2.72 SD, isoflurane +3.29 and +4.10 |
| The published apparatus's 50 ml dead space, as a ventilation decrement (below) | more than the wash-in rows allow | at the largest decrement they allow, desflurane is still −1.48 SD and both isoflurane cohorts leave their spread, at +1.68 and +2.17 |
| End-tidal sampling bias, a correction to the *published* value | an upward bias in the ratio, growing as solubility falls | struck: the one human measurement of the alveolar-to-arterial gradient points the other way (below) |
| Circuit-wall absorption, which this model's inert circuit walls leave out | the right direction, as in the sixth row | struck: the one study of a real circle system found desflurane close to the ideal curve at every flow (below) |

<!-- not-restated: 2.1 -->

The fourth row's volumes are round physiologic figures: 1 kg of lung tissue at
a tissue:blood ratio of 1.2, and 1.8 L of pulmonary and arterial blood. They only set how large
the added capacity is. They are not proposed as parameters. The added capacity equals 20.1% of
desflurane's fast pool, 19.7% of sevoflurane's and 23.4% of isoflurane's, about the same share
for all three. The fast pool is the alveolar gas, the venous blood and the vessel-rich group, and
`test_the_omitted_lung_store_is_the_share_of_the_fast_pool_printed` computes the three shares. But closing the residuals needs +2.41 gas-equivalent litres for desflurane and
−1.32 for isoflurane. The conclusion does not need precise volumes. Any capacity that scales
with blood solubility is the same *fraction* of every agent's fast pool. So adding it moves all
three rows together, and it cannot produce a residual in one agent alone.

**The sixth row simulated circuit-style rebreathing at an assumed ratio, and
the apparatus turns out not to be that shape at all.** The "Materials and
Methods" section of Yasuda 1991 *Anesthesiology* places about 50 ml of
corrugated Teflon between the tracheal sampling port and the nonrebreathing
valve. The paper states that this tubing protects the end-tidal sample from
contamination with inspired gas. At end-expiration the tubing contains
alveolar gas, and at end-inspiration it contains fresh gas. That makes it a
**series dead space**, not a mixing volume that returns a fraction of every
breath. In a model with one perfectly mixed alveolar compartment, the two are
different mechanisms.

Consider one breath during the elimination, with agent-free fresh gas. Let
$`V_D`$ be the total series dead space, anatomic plus apparatus. Inspiration
first pushes that $`V_D`$ of alveolar gas back into the alveoli. It then
follows with $`V_T - V_D`$ of agent-free gas. So the alveoli receive $`V_T`$
of gas carrying $`V_D F_A`$ of agent, and they expel $`V_T`$ carrying
$`V_T F_A`$. The net change is $`-(V_T - V_D) F_A`$. This is exactly this
model's $`\dot V_A (F_I - F_A)`$ at $`F_I = 0`$, provided that $`\dot V_A`$ is
the true alveolar ventilation $`(V_T - V_D) f`$. **So the published apparatus's
dead space is an alveolar-ventilation decrement of $`V_D f`$ and nothing
else.** The sixth row tested the dead space as a non-zero $`F_I`$. That would
describe this model's circuit, not Yasuda's apparatus.

**Modelled as a ventilation decrement, the dead space fails for the same reason
as the second row. It is the second row's mechanism, at a size taken from the
source.** The model has no respiratory rate, so the table runs the decrement
across the conventional range of rates for a paralysed, normocapnic adult. It
was simulated on 2026-11-21. For comparison, with no dead space at all,
desflurane sits at −2.33 SD:

| $`f`$ (/min) | $`\dot V_A`$ (L/min) | Desflurane | Isoflurane n=8 | Worst wash-in row |
| --- | --- | --- | --- | --- |
| 6 | 3.70 | −1.90 SD | +1.58 SD | −0.42 SD |
| 8 | 3.60 | −1.74 SD | +1.81 SD | −0.63 SD |
| 10 | 3.50 | −1.57 SD | +2.05 SD | −0.85 SD |
| 12 | 3.40 | −1.39 SD | +2.29 SD | −1.08 SD |

<!-- not-restated: 0.42 -->

The decrement moves desflurane the right way. It recovers between 0.43 and
0.94 SD of the 2.33 SD gap, which is a fifth to two fifths of it and never
the whole. The cost falls on the isoflurane cohort that was inside its spread
at +0.93 SD. The decrement pushes that cohort out to between +1.58 and +2.29
SD. The wash-in comparison sets its own ceiling. At 11 breaths per minute,
sevoflurane's wash-in row reaches −0.96 SD, and one more breath per minute
takes it outside its spread. So the largest decrement that the comparison
allows at all leaves desflurane 1.48 SD short, with both isoflurane cohorts
outside their spreads. The mechanism is **common-mode**, which means it moves
every cohort together. Desflurane's residual is differential, which means it
affects one agent alone.
`test_no_apparatus_dead_space_reaches_desflurane_s_published_elimination` and
`test_the_apparatus_dead_space_moves_every_cohort_together` assert both
halves, so this finding cannot go out of date without a test failing.

**It is still open whether the comparison should subtract the apparatus dead space.** Yasuda
derived the alveolar fraction of ventilation, $`f_A`$, from mixed expired gas,
$`F_M = f_A F_A + f_D F_I`$. The 1-l mixing chamber that supplies $`F_M`$ sits beyond the
nonrebreathing valve. The re-inspired 50 ml never reaches the chamber, so their $`f_A`$ is
$`(V_T - V_{D,\text{anat}} - V_{D,\text{app}})/V_T`$. That value already excludes the
apparatus dead space, so a comparison run at *their* alveolar ventilation must not subtract it
again. Neither paper reports that ventilation (below). This model runs at a default 4.0 L/min,
which has no primary source.
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->

**Neither paper publishes a ventilation.** Ventilation was titrated for each subject to
normocapnia, an end-tidal carbon dioxide of 5.5–6.5%. Minute ventilation was measured and used
in the mass balance. Even so, **no $`\dot V_E`$ and no $`f_A`$ is reported in either paper**,
and neither paper has a ventilation table. The *Anesthesiology* paper does give the definition
that the derivation above needs, in its description of the total-body-clearance method. Doses
delivered to the alveoli are computed as $`F_I \dot V_A \times 30`$ min "where
$`\dot V_A = f_A \dot V_E`$". So $`f_A`$ is the alveolar fraction of *total* minute ventilation.

**The nearest published analogue points the seventh row the wrong way.** The
paper reports pulmonary elimination clearances, $`V_1 k_{10}`$, for the eight
volunteers whose data give desflurane's residual. They are desflurane 4.11 ±
0.45, isoflurane 3.94 ± 0.34 and halothane 3.94 ± 0.33 L/min. The
seven-volunteer *Anesth Analg* cohort has 3.58 and 3.62 L/min. This model
runs at 4.0 L/min, so for the cohort in question it already matches the
study's own effective clearance. A dead-space decrement *lowers* alveolar
ventilation, which moves the model **away** from 4.11 rather than toward it.
This argument is independent of the common-mode argument, and it is stronger,
because it is specific to the one cohort that the mechanism would have to help.
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->
<!-- not-restated: 0.34 -->

**These clearances are a consistency check on the operating point and must not
be adopted as the operating point.** They were fitted to the same elimination
curves that this comparison is scored against, so running the model at them
would be circular. The paper itself also shows how precise they are. The same
eight subjects breathed all three agents at once from one cylinder. Their
ventilation was therefore physically identical across those three rows, yet
the fitted values still spread by about 4%.

**End-tidal sampling, the eighth table row, is struck** (project owner,
2026-09-13).

*What it proposed.* The published $`F_A`$ is end-tidal gas from an
anaesthetized volunteer. This model's $`F_A`$ is the fraction in one perfectly
mixed compartment. In a lung with ventilation-perfusion dispersion, a unit
with ventilation-perfusion ratio $`r`$ has
$`P_A/P_{\bar v} = \lambda_{b:g}/(\lambda_{b:g} + r)`$ during an elimination.
So the last units to empty carry the highest partial pressure during washout
and the lowest during wash-in. A washout-to-wash-in ratio would then be biased
upward, by an amount that grows as solubility falls. Take a log-normal
perfusion distribution at log SD 1.0 with a 5% shunt. On that distribution, this
model understates the arterial retention, which it fixes at
$`\lambda_{b:g}/(\lambda_{b:g} + \dot V_A/Q)`$, by 44% for desflurane, 30% for
sevoflurane and 15% for isoflurane. That is the same rank order as the
residuals, which is what made the hypothesis attractive.
<!-- not-restated: 5 % -->

*What the methods sections settled in its favour.* The fifth table row rules
out the reading in which the published value is a **flow-weighted** alveolar
fraction. So the hypothesis rested entirely on the published $`F_A`$ being an
end-tidal sample instead. The "Materials and Methods" section of Yasuda 1991
*Anesthesiology* places that sampling port **at the tracheal tube**. The 50 ml
of Teflon that the seventh row analyses is interposed to protect the sample
from inspired gas. The paper samples mixed expired gas **separately**, from the
1-l mixing chamber, and reports it as $`F_M`$. So the quantity that the fifth
row excludes is $`F_M`$, not $`F_A`$. The fifth row therefore does not rule the
hypothesis out.

*What struck it.* The one primary human measurement of that gradient disagrees with the
hypothesis on both counts. Yasuda's own discussion flags the assumption "that the $`F_A`$
accurately indicates the anesthetic partial pressures in arterial blood". It cites Carpenter RL,
Eger EI II, *Alveolar-to-arterial-to-venous anesthetic partial pressure differences in
humans*, Anesthesiology 1989;70(4):630–5, PMID 2930000. That study sampled arterial blood,
end-tidal gas and inspired gas simultaneously in eight surgical patients.

- **Solubility runs the other way.** Measured $`P_A/P_a`$ is 1.23 ± 0.13 for
  halothane and 1.11 ± 0.09 for isoflurane, P = .009. The authors state the
  rule: the difference "should be greater with anesthetics having higher
  blood solubility". Desflurane is the least soluble agent in the comparison.
  So it should show the *smallest* gradient, where the hypothesis needs the
  largest.
- **The sign reverses through an elimination.** The mechanism is
  contamination of the end-tidal sample by physiologic dead space gas, which
  the authors call "unchanged inspired gas". The fitted relation is
  $`(P_A - P_a) = 0.22 (P_I - P_a) + 0.02`$. The authors interpret its slope
  as the sample being about 20% dead space gas. The bias therefore follows
  $`F_I`$. It is upward during administration, where $`F_{A0}`$ is measured,
  and **downward through an elimination run at $`F_I = 0`$**. Both push the
  published $`F_A/F_{A0}`$ *down*. So the measured 0.140 understates the true
  arterial ratio, and this model's 0.0934 sits further from the true ratio,
  not nearer.

*Two limits of that measurement, neither enough to revive the hypothesis.*

- Carpenter's regression was fitted over positive $`P_I - P_a`$ only, never
  at $`F_I = 0`$. Applying it to an elimination therefore extrapolates the
  mechanism, not the fitted line.
- His patients were 52 ± 16 years old, against Yasuda's 25 ± 5, and
  physiologic dead space depends on age.

For the hypothesis to hold, both limits would have to resolve in its favour,
and the measured solubility ordering would also have to reverse. Yasuda's 50 ml
guard does not settle the question either. It protects against contamination
from the **apparatus**, whereas Carpenter's 20% is physiologic dead space inside
the patient.

**Circuit-wall absorption, the ninth table row, is struck by the paper behind the circuit
volume.** Targ, Yasuda and Eger measured washin at 0.5–2 L/min and washout at 1–5 L/min in a
real conventional circle system. They compared both against the ideal exponential (*Anesth
Analg* 1989 Aug;69(2):218–25, PMID 2764290). Desflurane's curves lay close to the ideal line at
every flow. They deviated most at the lowest flows and near complete washin, and the comparison
here runs at neither. The authors conclude that absorption of desflurane "by circuit
components or soda lime should not hinder induction of or recovery from anesthesia". So for
**desflurane**, this measurement most nearly supports the model's inert circuit, and it strikes
the candidate.
<!-- not-restated: 5 L/min -->

**The direction does not rule it out, because a store that this model leaves out would move
the comparison toward the published value.** A wall that dissolves agent during a 30-minute
administration gives it back during the washout. That keeps the circuit fraction high, and
with it the inspired fraction, which *slows* the alveolar fall. Desflurane's residual is this
model washing out too **fast**, with the apparatus removed. A wall in the published apparatus
would have raised the published ratio above what an inert apparatus gives, which matches the
residual's sign. The sixth table row shows the same direction for rebreathing, which also
returns agent to the inspired gas. Two other grounds rule the candidate out for desflurane:
the measurement above, and the published apparatus having no circle system (the bullet on
sevoflurane and isoflurane below). This model has no wall term, so a test cannot vary one. The
circuit volume is the model's only store on the circuit side. A test checks that, for every
agent, the five-minute $`F_A/F_{A0}`$ rises at each step as the circuit volume goes from half
to twice its stored value. That direction is what rules the candidate out for sevoflurane and
isoflurane, below.

**The same study finds that a real circuit measurably retards sevoflurane and
isoflurane. That is a limitation of this simulator, but it is not a candidate
here, for three separate reasons, any one of which is sufficient.**

- **`docs/MODEL.md` § "Absorption by the circuit" already records it.** That section gives the
  coefficient table and its ranking, which make the inert circuit most nearly true for
  desflurane and least true for halothane. `ROADMAP.md` § "Planned milestones" records that no
  wall term is planned. Counting it here would suggest that the residual is partly explained,
  and it is not.
- **The departure it would be offered to explain is in the elimination rows,
  not the wash-in rows.** Sevoflurane's +3.79 SD and isoflurane's +4.15 SD are
  five-minute $`F_A/F_{A0}`$ figures. The wash-in comparison has no departure
  for anything to explain. Every agent stays inside its published spread at
  every fresh gas flow from 1 to 10 L/min.
- **On the elimination rows the mechanism moves the wrong way, and it is
  absent from the published measurement besides.** Most of that departure is
  already attributed to the breathing system. Removing the rebreathing takes
  sevoflurane to −0.15 SD and isoflurane to +0.65 SD. Wall absorption is a
  *further* store that returns agent to the circuit during the washout. Adding
  it would keep $`F_I`$ high for longer and push both rows further above their
  means, not toward them. The direction rules the candidate out for these two
  agents because the departure it would explain is the model washing out too
  slowly, the opposite of desflurane's residual. They are also the two agents
  for which wall absorption is strongest. The published cohorts also breathed
  from a non-rebreathing apparatus, whose design puts the potent agents'
  inspired fraction at or near zero. So no circle-system wall effect is present
  in the published number at all.

<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- not-restated: 0.65 -->

Whatever the explanation is, it has to fit the whole published set and not
desflurane alone. The same eight volunteers gave a halothane ratio of
0.25 ± 0.02. Halothane's blood:gas coefficient is conventionally about 2.4.
That is a textbook figure, not a parameter this project stores. So across a
roughly six-fold range of solubility, the published five-minute ratios span
only 0.14 to 0.25. That spread is narrower than a perfusion-limited model
produces.
<!-- not-restated: 2.4 -->

**So the cause is not identified. The disagreement's sign and size are
known.** The vessel-rich coefficient and the nine candidates in the table above
are each ruled out, for the reasons given above. What remains must be a
mechanism that acts on the least soluble agent alone and keeps its alveolar
fraction high. **One candidate remains, and this
project cannot test it:**

1. *The published value.* Desflurane's recovery, the agent recovered divided
   by the agent taken up, was 105 ± 25% in those eight volunteers. Isoflurane,
   measured in the same sitting, had 102 ± 13%. Desflurane's figure has the
   wider spread of the two, and it is centred above complete recovery.

`test_no_measured_tissue_solubility_reaches_desflurane_s_published_elimination` checks the
vessel-rich coefficient claim, and `test_a_larger_circuit_can_only_slow_the_elimination` checks
the circuit-volume direction. Candidate-table rows four to six were computed by an independent,
simple fixed-step (forward-Euler) integration of these equations. With no shunt, it puts
desflurane at −2.29 SD, against the shipped driver's −2.33. The seventh row used the shipped
driver. `data/patients/reference_adult.json` records the 4.0 L/min alveolar ventilation as a
program default. Both Yasuda papers, Carpenter 1989, and Targ 1989 were read at full text on
2026-09-13. Targ 1989 is also cited for the circuit volume, and for the inert circuit in
`docs/MODEL.md` § "Absorption by the circuit".
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->

#### The early wash-in curve against the published figures

**Over the first 25 minutes, sevoflurane and isoflurane follow the published
wash-in curves within one SD** (simulated 2026-11-21). Desflurane's $`F_A/F_I`$
runs 0.032 to 0.042 above its published curve from 1 to 10 minutes, and agrees
from 12.5 minutes on. This early gap is a known limitation of the model. The
model is compared with each curve point by point because $`F_A/F_I`$ at 30
minutes alone would barely show an error in the lung's gas volume or the circuit.

Neither paper tabulates its $`F_A/F_I`$ curve, so the published values were read
from page scans of each paper's Figure 2. Both figures plot the curve during
administration as mean ± SD, with each SD drawn on one side of the marker. Each
30-minute point read from them lies within 0.006 of the value stated in the
paper's text, so a reading error here is about 0.006. Three of the 1-minute SDs
are hidden among overlapping marks near the axis, so the comparison uses the
next readable SD of the same cohort instead. A separate note records how the
figures were read and every value taken from them
(`docs/references/yasuda-1991-figure-2-wash-in.md`).

**The comparison holds $`F_I`$ fixed from the start, which no setting of the
simulator does.** Both papers gave the agents as a square wave from a
non-rebreathing circuit, so $`F_I`$ was the cylinder's fraction from the first
breath (*Anesth Analg* p. 317, *Anesthesiology* p. 490). The simulator's circuit
instead fills at its own time constant, so its $`F_I`$ lags the dial for the
first minute or more. In every other respect, the comparison runs the simulator
as released.

Simulated on 2026-11-21, as the model's distance from each published mean, in
units of that point's SD:

| Cohort | 1 to 3 min | 5 min | 7.5 to 25 min |
| --- | --- | --- | --- |
| Sevoflurane, n=7 | −0.54 to −0.69 SD | −0.22 SD | +0.48 to +0.77 SD |
| Isoflurane, n=7 | −0.69 to −0.83 SD | −0.18 SD | +0.34 to +0.76 SD |
| Isoflurane, n=8 | −0.59 to −0.67 SD | +0.08 SD | +0.32 to +1.06 SD |
| Desflurane, n=8 | +1.80 to +1.83 SD | +1.83 SD | +1.71 SD at 7.5 min, +2.10 SD at 10 min, then +0.95 to +0.28 SD |

<!-- not-restated: 0.34 -->

<!-- not-restated: 0.54, 0.76, 2.10, 0.18 -->

**The model's sevoflurane and isoflurane curves sit a little below the published
ones in the first 3 minutes and a little above from 7.5 minutes on.** Their only
point beyond one SD is isoflurane at 12.5 minutes, +1.06 SD, which is within a
reading error of one SD.

**The desflurane gap likely comes from something that only desflurane has**,
such as its blood:gas or a tissue:gas coefficient. The model's settings are an
unlikely cause, because the eight volunteers in the desflurane cohort breathed
isoflurane from the same cylinder as desflurane, and the model follows their
isoflurane curve. An error in ventilation or lung volume would move every agent
the same way, but sevoflurane and isoflurane sit slightly below their curves
early on.

**No single stored coefficient closes the gap when it is varied only within its
measured range** (simulated 2026-10-18). The runs changed one desflurane
coefficient at a time and left every other value as stored:

- **Blood:gas is the only coefficient that brings the early points within one
  SD, and it does so only at values where the 30-minute comparison fails.** The
  1-to-10-minute points come within one SD once blood:gas is about 0.55 or
  higher. Eger's 0.424 ± 0.024 falls short of 0.55 even at the edge of its
  spread. Esper et al. 2015 measured 0.57 ± 0.04 in surgical patients, and at
  0.57 every point from 1 to 10 minutes lies within 0.83 SD. But the 30-minute ratio stays
  within one SD at every fresh gas flow from 1 to 10 L/min only while blood:gas
  is about 0.46 or lower. At 0.57 it falls outside one SD at every flow, from
  −1.35 SD at 10 L/min to −2.61 SD at 1 L/min. Raising blood:gas to 0.57 moves
  desflurane's open-circuit 5-minute washout ratio only from −2.33 SD to
  −1.97 SD.
- **The vessel-rich and muscle coefficients cannot close the gap** at any value
  within Yasuda et al. 1989's measurements (brain 0.54 ± 0.02, muscle
  0.94 ± 0.35).

<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- not-restated: 0.54 -->

No stored value is changed. Using Esper's blood:gas value for desflurane alone
would mix coefficients from two sources. Esper's values for all three agents
would put the sevoflurane and isoflurane points in the first 3 minutes 1.0 to
1.4 SD below their curves. The stored values would be weighed again in the
planned primary-literature coefficient set (`ROADMAP.md` planned-milestone item 31).

**The model has no second-gas effect, and the early curve is where one would
show first.** Caveat 1 above applies here too. The effect's size in these
volunteers was not measured. They had breathed 70% nitrous oxide for 30 minutes
before the potent agents started, and 65% throughout, so their nitrous oxide
uptake was already low and the effect was probably small.

The comparison runs in a driver that only the tests use
(`_clamped_wash_in()` in `tests/reference/test_published_wash_in_and_elimination.py`).
Before the first step, the driver enlarges the circuit to the largest volume
that the model accepts, because it can set the circuit back only once a second.
Before the first step and after every step, it sets the circuit back to the fixed $`F_I`$ and
records the agent it adds or removes, so the model's check that the amount of
agent is conserved still passes.

The five desflurane points from 1 to 10 minutes and the isoflurane point at 12.5
minutes are checked against a regression band, from −1 to +2.5 SD, instead of within one SD. A regression band guards the model's own result against change and claims no agreement with the data. The band's upper edge is above desflurane's largest distance in the table
above, so the gap cannot grow past +2.5 SD without a test failing.

#### What the published-data gate can and cannot resolve

**For most stored values, passing the published-data gate rules out only large
errors** (from model runs on 2026-10-18). The published-data gate is the set of checks that
compare the model with published measurements in people. A pass does rule out a
model whose structure is wrong.

The published-data gate contains the early wash-in points from 1 to 25 minutes, run with F_I
held at the airway (§ "The early wash-in curve against the published figures"
above). It also contains the 30-minute wash-in band for each cohort at every
fresh gas flow from 1 to 10 L/min, the sign of the elimination disagreement for
each cohort, and both solubility orderings.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

The regression pins are not part of the published-data gate, because they compare the model
with its own output. They include the 5-minute elimination pin above, the
late-washout tables, and the reference states recorded
in `tests/reference/test_coupled_dynamics.py` (`PINNED_REFERENCE_STATES`). A pin
fails on any change at all, so it catches an accidental edit. It cannot show
whether a comparison with published data would have caught a wrong stored value,
so no pin may be cited as validation of a stored value.

##### How far one stored value can change before the gate fails

Each cell of the table below covers one stored parameter for one agent. It gives
the lower and upper edges of the range of change over which the published-data gate still
passes (from model runs on 2026-10-18, and on 2026-11-21 for the edges that the early
wash-in points set). Each parameter was varied from a tenth
to four times its stored value, with every other value unchanged. The edges
were found to the nearest half a percentage point. An edge marked "past", such
as "past −90%", means that the published-data gate still passed at a tenth or at four times the
stored value.

| Stored parameter | Sevoflurane | Isoflurane | Desflurane |
| --- | --- | --- | --- |
| Blood:gas coefficient | −5% / +5% | −1% / +5% | −1% / +10% |
| Vessel-rich tissue:gas, or vessel-rich volume | −15% / +15% | −3% / +11% | −6% / +55% |
| Muscle tissue:gas, or muscle volume | −43% / +102% | −16% / past +300% | −11% / +105% |
| Fat tissue:gas, or fat volume | past −90% / past +300% | past −90% / past +300% | −84% / past +300% |
| Venous pool volume | past −90% / +88% | −47% / +61% | −78% / past +300% |
| Alveolar gas volume (FRC) | past −90% / +20% | −37% / +22% | −8% / +33% |
| Circuit volume | past −90% / +76% | past −90% / +253% | −85% / +98% |

<!-- not-restated: 5 %, 8 % -->

The first row's percentages apply to the stored blood:gas coefficients: 0.65
for sevoflurane, 1.3 for isoflurane and 0.42 for desflurane. The tissue:gas
coefficients stay as shipped when blood:gas changes, so each tissue:blood
coefficient moves inversely, as it would if the stored blood:gas value alone
were wrong.
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
<!-- provenance: data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3 -->
<!-- provenance: data/agents/desflurane.json blood_gas_partition_coefficient = 0.42 -->

A tissue's volume and its tissue:gas coefficient give the same edges, because a
run depends only on their product, the tissue's capacity.

**The table supports these conclusions about a pass of the published-data gate:**

- **A narrow edge is not a narrow uncertainty.** Most of the narrowest edges
  come from the 12.5- and 15-minute points, where the shipped model already sits
  at +0.75 to +0.95 SD. There, a change that raises the curve by a few tenths of
  an SD takes it past the published-data gate's limit of +1 SD. So isoflurane's −1% edge for
  blood:gas means that the shipped model has little room left there, not that
  the stored coefficient is known to 1%. The published figure can be read to
  about 0.3 SD, so an edge reached by a smaller movement of the curve is within
  the reading error.
- **For sevoflurane and isoflurane, the published-data gate detects both a rise and a fall in
  blood:gas and in the vessel-rich group.** The edges lie between 1% and 15%.
  The 12.5- and 15-minute points set every lower edge. The 2- and 3-minute
  points set isoflurane's upper blood:gas edge and both agents' upper
  vessel-rich edges. The 30-minute wash-in band at 1 L/min sets the other upper
  edges, and most of desflurane's.
- **The published-data gate detects an alveolar gas volume that is too large.** Making the
  volume a fifth to a third larger slows the first minute of wash-in enough to
  take it outside one SD for every agent. Doubling the volume moves
  sevoflurane's 1-minute F_A/F_I from 0.538 to 0.429, which is −2.85 SD. The
  published-data gate does not detect a smaller volume for sevoflurane.
- **Desflurane's edges reflect its disagreement with the published data.**
  Its points from 1 to 10 minutes sit at +1.7 to +2.1 SD. They are checked
  only against a looser regression band, which ends at +2.5 SD. So its −8% lower edge for
  alveolar gas volume is set by that band, not by a limit of one published SD.
- **The published-data gate detects no change at all in fat for sevoflurane or isoflurane.**
  That is expected of checks that cover 30 minutes of wash-in and 5 minutes of
  washout. Fat solubility and fat volume set the hours-long tail of washout,
  from which a learner judges emergence. Nothing here checks them against a
  measurement. § "The first 24 hours of elimination against the published
  mean curves" compares that tail with the published fits, but does not
  require the two to agree.
- **The published-data gate constrains muscle only loosely.**
- **The published-data gate does not detect a smaller circuit** for sevoflurane or isoflurane,
  down to a tenth of the stored value. The early points are run with F_I held
  at the airway, so the circuit does not affect them.

<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

<!-- not-restated: 2.1, 8 % -->

**Two tests keep the table in step with the code.** One fails if the published-data gate stops
detecting a change that it detects today. The other fails if the published-data gate starts to
detect a change that this section says it cannot.

The test that expects the published-data gate to fail checks every agent at blood:gas ×0.90
and ×1.15, vessel-rich tissue:gas ×0.80 and ×1.75, and alveolar gas volume
×1.50 (`test_the_published_data_gate_fails_at_a_stated_perturbation`). It does
not use ×1.10 for blood:gas, because that is too close to desflurane's edge at
×1.097.
<!-- not-restated: 1.10 -->

The test that expects the published-data gate to pass checks every agent at fat tissue:gas
×0.50 and ×2.00, muscle tissue:gas ×1.50 and circuit volume
×0.50 (`test_the_published_data_gate_passes_at_a_stated_perturbation`). It
checks fat volume ×2.00 for sevoflurane only, because a tissue's volume and its
tissue:gas coefficient change a run identically. It also checks alveolar gas
volume ×0.50 for sevoflurane, venous pool volume ×0.50 for sevoflurane and
desflurane, and venous pool volume ×2.00 for desflurane. For those three, the
other agents have an edge at or inside the factor.

Each factor in the two tests sits well clear of its edge, because a test placed
at an edge would be 0.01 to 0.03 SD from flipping. Both tests run the published-data gate at
its shipped limit (`AGREEMENT_TOLERANCE_SD`). The limit is the published
spread, not the band.

##### Which stored values each ratio responds to

The wash-in ratio at 30 minutes and the elimination ratio at 5 minutes respond
to almost separate sets of parameters, which is why the edges fall where they
do. The table below shows how far each ratio moves when one coefficient is
raised by 10%, in units of that ratio's own published SD. The figures come
from model runs on 2026-11-22, against each agent's first cohort. For
isoflurane that is the Anesth Analg 1991;72:316-24 cohort, not the
Anesthesiology 1991;74:489-98 one:

| Perturbed coefficient | Wash-in | Elimination |
| --- | --- | --- |
| Blood:gas | −0.57 to −0.64 | +0.11 to +0.18 |
| Vessel-rich tissue:gas | −0.02 to −0.07 | +0.44 to +0.54 |
| Muscle tissue:gas | −0.08 to −0.15 | −0.09 to −0.12 |
| Fat tissue:gas | −0.00 | −0.00 |
<!-- not-restated: 0.18, 0.54 -->

Wash-in at 30 minutes depends mostly on blood:gas and barely on the vessel-rich
group. Elimination at five minutes depends mostly on the vessel-rich group and
barely on blood:gas. This fits the rebreathing explanation above. The circuit
sets *where* the elimination ratio sits against the published mean, as an
offset fixed by the reference settings.

#### The first 24 hours of elimination against the published mean curves
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**This subsection compares the model's late washout with the published curves, alongside the published-data gate above. It is not
a second gate** (2026-09-27). Caveat 4 keeps the five-minute comparison out of
the papers' multi-day curves, because over those hours a compartment that this model lacks
carries the measured washout. So a comparison there shows an omission rather than a
parameter. This subsection gives the size of that omission, the hour from which it appears and
the direction in which it points. Every check here is one of three kinds. None claims agreement
with a human washout, and none may be restated as one.

1. A regression band around what the test computed. The runs date from
   2026-09-27, or from 2026-10-03 for the muscle group's variation and the open
   circuit's modes below. Every value from the stepped open-circuit run was
   computed again on 2026-11-21.
2. The conclusion that such a band supports.
3. A property of the published coefficients.

**What is compared, and under what conditions.** Both papers fit each
volunteer's elimination to a sum of five exponentials,
$`F_A/F_{A0} = \sum_i A_i e^{-t/\tau_i}`$. Each paper publishes the mean and
SD of every coefficient in its Tables 1 and 2 (*Anesth Analg* p. 321,
*Anesthesiology* pp. 494-95). The curve built from the mean coefficients is compared as
published. Its amplitudes sum to 0.912 to 0.936 rather than 1 at discontinuation, because they
are means of per-subject fits. Scaling them to sum to 1 would raise every fitted value by 7 to
10%, and lower every ratio below by 6 to 9%. The model runs the protocol of the five-minute elimination comparison in
§ "Published wash-in and elimination validation test": the
shipped 30-minute wash-in at the reference settings, then the vaporizer closed for 23.5 hours.
So the run ends at the supported run length of 24 hours. Its fifth minute matches the five-minute
ratios that the elimination regression pins hold, so the tables continue that comparison rather than starting a
second protocol. The comparison uses the same two conditions as those pins and no others. *Shipped* is the
rebreathing circuit at 10 L/min, which gives the tail that the chart draws. *Open circuit* is
the test-only condition that discards the circuit's contents after every step, and no setting
of the simulator can produce it. The table times are the papers' own sampling times within the
first day (*Anesth Analg* p. 317), chosen because the fit passes near a measured sample at
each. The run's last minute, 1410 min, is added.
<!-- not-restated: 10 L/min -->
<!-- not-restated: 24 hours -->

**The result, as model over fit.** The cohorts are in the order sevoflurane
and isoflurane from *Anesth Analg*, then desflurane and isoflurane from
*Anesthesiology*.
`test_the_first_24_hours_of_elimination_against_the_published_mean_curves`
checks every entry to within 1%, and every crossing hour below to within
0.1 h. The shipped table comes from runs on 2026-09-27, and its 1410-minute row from runs on
2026-10-17. The open-circuit table comes from runs on 2026-11-21:

| Minutes | Sevoflurane, shipped | Isoflurane, shipped | Desflurane, shipped | Isoflurane (second study), shipped |
| ---: | ---: | ---: | ---: | ---: |
| 5 | 1.20 | 1.33 | 1.11 | 1.42 |
| 30 | 0.61 | 0.71 | 0.75 | 0.88 |
| 60 | 0.81 | 0.87 | 0.93 | 1.08 |
| 120 | 1.01 | 1.07 | 1.11 | 1.33 |
| 240 | 1.20 | 1.26 | 0.88 | 1.52 |
| 400 | 1.02 | 1.07 | 0.55 | 1.23 |
| 600 | 0.74 | 0.78 | 0.56 | 0.86 |
| 800 | 0.67 | 0.68 | 0.80 | 0.74 |
| 1400 | 1.23 | 1.11 | 2.09 | 1.15 |
| 1410 | 1.24 | 1.12 | 2.11 | 1.16 |

| Minutes | Sevoflurane, open circuit | Isoflurane, open circuit | Desflurane, open circuit | Isoflurane (second study), open circuit |
| ---: | ---: | ---: | ---: | ---: |
| 5 | 0.79 | 0.98 | 0.64 | 1.05 |
| 30 | 0.43 | 0.51 | 0.53 | 0.63 |
| 60 | 0.58 | 0.64 | 0.65 | 0.79 |
| 120 | 0.70 | 0.77 | 0.76 | 0.95 |
| 240 | 0.81 | 0.85 | 0.58 | 1.03 |
| 400 | 0.67 | 0.69 | 0.36 | 0.78 |
| 600 | 0.47 | 0.48 | 0.37 | 0.53 |
| 800 | 0.43 | 0.42 | 0.54 | 0.46 |
| 1400 | 0.81 | 0.71 | 1.39 | 0.74 |
| 1410 | 0.82 | 0.72 | 1.41 | 0.75 |

<!-- not-restated: 0.36 -->

<!-- not-restated: 0.65, 0.76, 0.42, 0.54 -->

The next table gives the hours at which the shipped tail crosses the fitted
curve, and how far from the curve the tail sits between crossings:

| Cohort | Below from | Above from | Below from | Above from | Widest below, middle stretch | At 23.5 h |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sevoflurane | 0.13 h | 1.98 h | 6.88 h | 20.65 h | 0.67 at 12.9 h | 1.24 |
| Isoflurane | 0.17 h | 1.62 h | 7.33 h | 21.78 h | 0.68 at 13.5 h | 1.12 |
| Desflurane | 0.10 h | 1.30 h | 3.38 h | 15.30 h | 0.51 at 8.1 h | 2.11 |
| Isoflurane (second study) | 0.22 h | 0.78 h | 8.42 h | 21.05 h | 0.74 at 13.7 h | 1.16 |

In the open circuit, the tail falls below the fitted curve between the second
and the sixth minute. For sevoflurane and the first study's isoflurane, it
stays below the curve for the whole run. Desflurane rises back above the
curve at 19.18 h. The second study's isoflurane sits above the curve between
2.45 and 4.57 h, by 5% at most. After the first hour, the open-circuit tail
falls as low as a third to a half of the mean curve in every cohort (0.34 to
0.46), near hour 8 for desflurane and near hour 13 for the others. Sevoflurane's
tail is lower only in the first half hour, at 0.36 near minute 19.
<!-- not-restated: 5 % -->
<!-- not-restated: 0.34 -->
<!-- not-restated: 0.36 -->

**Read in stretches.** The shipped tail sits above the fitted curve at five
minutes. That excess is the apparatus term that the five-minute elimination comparison records. The tail
falls below the curve from 6 to 13 minutes until 0.8 to 2.0 hours. At the
widest, around 15 to 25 minutes, it is 15 to 44% below. It then runs above
the curve until 3.4 hours for desflurane and 6.9 to 8.4 hours for the other
three, by 12 to 52% at the widest. From there it runs *below* the curve until
15.3 hours for desflurane and 20.7 to 21.8 hours for the others. At the
widest it is a third below, near 13 hours, and for desflurane it is a half
below, near 8 hours. It finishes above the curve, by 12 to 24% at 23.5 hours
and by a factor of 2.1 for desflurane. The middle stretch answers the
question that `docs/MODEL.md` § "Intertissue diffusion: the missing fourth
compartment" asked. In every fitted curve, the fourth compartment's term is the
largest over most of these hours, which that section gives. This model has no
such term.
Over those hours its tail falls faster than the measured mean. With the
apparatus gone, it does so from the start. In the shipped condition, it does
so only from the seventh hour. Until then the rebreathing circuit and the
muscle group's slow return, described below, hold the tail above the curve.
With the circuit's return taken away, the same hours sit at or below the
curve.
<!-- not-restated: 2.1 -->

The model's muscle group returns agent more slowly than the fitted muscle
term does. That is why the ratio of model to fit peaks in hours 2 to 4. In
the open circuit, this peak is the tail's closest approach to the curve. In
the shipped condition, it is the tail's furthest excess over the curve. A
fitted time constant is an apparent one, read off the whole curve, so the model's terms are
read off its own curve in the same way (2026-10-03). They are the exponential components of the
open-circuit model, which is the five equations of `docs/MODEL.md` § "Equations" with nothing
inspired. The table gives each term as its time constant in minutes and its amplitude in
percent of $`F_{A0}`$, with the cohorts in the same order as the tables above. A test checks
the model's terms to within 0.2%:

| Term | Sevoflurane | Isoflurane | Desflurane | Isoflurane (second study) |
| --- | ---: | ---: | ---: | ---: |
| Muscle, model | 155 min, 2.37% | 161 min, 4.31% | 92.6 min, 2.47% | 161 min, 4.31% |
| Muscle, fitted | 81.7 min, 4.60% | 85.0 min, 7.19% | 48.9 min, 4.86% | 80.0 min, 5.93% |
| Fat, model | 2650 min, 0.060% | 2860 min, 0.12% | 1540 min, 0.063% | 2860 min, 0.12% |
| Fat, fitted | 2230 min, 0.028% | 2310 min, 0.072% | 1350 min, 0.031% | 2110 min, 0.080% |

So the model's muscle term is 1.89 to 2.02 times as slow as the fitted one,
and 0.51 to 0.73 times as large. Its fat term is 1.14 to 1.36 times as slow
and 1.5 to 2.1 times as large. The fitted fat amplitudes in that comparison
have SDs that are 53 to 94% of their means. A group's isolated time constant is its tissue
volume times the tissue:gas coefficient, divided by its blood flow times the blood:gas
coefficient (`docs/MODEL.md` § "Tissue groups"). The reference adult has 33 L of muscle perfused at 0.9 L/min and 14.5 L of fat
perfused at 0.3 L/min. On these values, the isolated constants for sevoflurane, isoflurane and
desflurane are 135, 127 and 84.7 minutes for muscle, and about 2500, 2600 and 1500 minutes for
fat. Each is shorter than the group's apparent constant. The arterial blood that reaches a
group during the washout still carries agent, because the lungs do not exhale all of the agent
in each group's return, and the rest goes round again. So a store empties more slowly than its
own blood flow alone would empty it, and the isolated constant understates how slow the
model's term is.
<!-- derived: 135 minutes from data/patients/reference_adult.json tissue_groups.muscle.volume_l = 33.0, tissue_groups.muscle.perfusion_fraction = 0.18, default_cardiac_output_l_min = 5 -->
<!-- derived: 135 minutes from data/agents/sevoflurane.json tissue_gas_partition_coefficients.muscle = 2.4, blood_gas_partition_coefficient = 0.65 -->
<!-- derived: 127 minutes from data/agents/isoflurane.json tissue_gas_partition_coefficients.muscle = 4.5, blood_gas_partition_coefficient = 1.3 -->
<!-- derived: 84.7 minutes from data/agents/desflurane.json tissue_gas_partition_coefficients.muscle = 0.97, blood_gas_partition_coefficient = 0.42 -->
<!-- derived: 2500 minutes from data/patients/reference_adult.json tissue_groups.fat.volume_l = 14.5, tissue_groups.fat.perfusion_fraction = 0.06, default_cardiac_output_l_min = 5 -->
<!-- derived: 2500 minutes from data/agents/sevoflurane.json tissue_gas_partition_coefficients.fat = 34.0, blood_gas_partition_coefficient = 0.65 -->
<!-- derived: 2600 minutes from data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70.0, blood_gas_partition_coefficient = 1.3 -->
<!-- derived: 1500 minutes from data/agents/desflurane.json tissue_gas_partition_coefficients.fat = 13.0, blood_gas_partition_coefficient = 0.42 -->
<!-- not-restated: 2.1 -->

The claim that the muscle group's slow return places this peak in hours 2 to 4
was tested on 2026-10-03. The group's tissue:gas coefficient was lowered to
0.58 to 0.67 of its stored value, with everything else as stored. This change
makes the group's isolated time constant equal to the fitted one, and its apparent time
constant 1.09 to 1.28 times the fitted one. Over a 30-minute wash-in the group is far from
equilibrium. It takes up agent about as fast as its blood flow brings it, whatever its
capacity. So it contains only 4 to 10% less agent at discontinuation, and the change mainly
alters how fast that store comes back. With the change, in six-hour runs, the open-circuit peak
comes at 0.62 to 1.45 hours instead of 2.17 to 3.92. At four hours the tail is 0.50, 0.62, 0.24
and 0.70 of the fitted curve, instead of 0.81, 0.85, 0.58 and 1.03. The shipped peak comes at
0.65 to 1.97 hours instead of 2.27 to 4.15. The tail lies above the curve until 1.6, 3.7 and
4.5 hours instead of 6.9, 7.3 and 8.4. With the change, desflurane's tail never rises above the
curve.
<!-- not-restated: 0.65 -->

The late excess is due to the model's larger and slower fat term, and it is
still growing when the run ends. The ratio rises between minutes 1400 and 1410
in every cohort and in both conditions. It grows because the fitted curve is
still falling on the fourth compartment's time constant, while the model is
already falling on its fat term's.

**Three limits on how far these results can be read.**

1. *The fitted mean curve is not the measured mean, and where it can be
   checked it runs high.* Five minutes is the one time at which both are
   published. There, the mean coefficients give 0.194, 0.243, 0.147 and 0.228,
   against measured means of 0.157 ± 0.020, 0.223 ± 0.024, 0.14 ± 0.02 and
   0.22 ± 0.02. The fitted values are above the measured ones by
   1.84, 0.83, 0.33 and 0.39 published SD, or by 3.5 to 24%
   (`test_the_fitted_mean_curves_run_above_their_own_measured_five_minute_means`).
   A sum of exponentials built from mean coefficients over-states the mean of
   the subjects' curves wherever a time constant varies between subjects.
   Every one of these time constants does vary, with SDs of 10 to 52% of the
   means. So every ratio above understates the model against the volunteers'
   mean. At the one point where the size of that understatement can be
   measured, it is 3.5 to 24%. For sevoflurane, the open-circuit model sits
   0.15 SD below the measured five-minute mean and 20% below the fitted curve
   at the same instant. The whole of that 20% comes from the fit itself.
   Nothing here corrects for this, because no measured mean exists at the
   later times to correct against. Both papers plot those later means
   (Figures 3 and 4), but on logarithmic axes from which no number was taken.
2. *The term that carries the measured curve over the middle stretch is as
   uncertain between subjects as it is large.* The fourth compartment's
   amplitude is 0.717 ± 0.800, 1.296 ± 1.237, 0.775 ± 0.482 and 1.125 ± 0.669
   (×100). Those SDs are 59 to 112% of the means. So a tail that lies a third
   to a half below the mean curve over those hours is inside the spread of the
   volunteers' own curves. The direction and the mechanism are settled. The
   model has no term there, and in the open circuit the model's tissue return
   alone falls to a third to a half of the mean. The size is known to about a factor
   of two, and no better.
3. *The published subjects breathed nitrous oxide throughout, and the
   parameters under test descend from the lineage of the data.* These are
   caveats 1 and 2 of § "Published wash-in and elimination validation test",
   unchanged.

**How much of the gap sevoflurane's missing metabolism could account for:
little, and in the wrong direction over the middle stretch.** This model has no
metabolism (`docs/MODEL.md` § "Known limitations"). A human does, and for sevoflurane it is
2 to 5% of the absorbed dose (Kharasch 1995, cited under
`docs/INTERFACE.md` § "Supported run length"). The module has a first-order sink on the
vessel-rich group that is used only in tests. The sink is placed where the
papers' own mammillary model places hepatic elimination: "the second
compartment (vessel-rich group; k20)", *Anesth Analg* p. 318. It runs at that
paper's fitted sevoflurane rate constant, k20 = 0.0094 min⁻¹ (Table 3,
p. 321). The SD of that constant is 0.0171, so the cohort could not tell it
from zero. The sink runs during the
administration as well as the elimination, because a human's metabolism does.
In this model, by the end of the run, the sink removes 7.8% of the 30-minute
uptake in the shipped condition and 7.1% in the open circuit. Both figures are
above Kharasch's range, which is what makes the sink's effect a bound. The sink
lowers the shipped tail by 4.5% at five minutes and by 1.9 to 2.9% from 30
minutes on. It lowers the open tail by 5.0% and then by 1.3 to 1.8%
(`test_sevoflurane_s_missing_metabolism_moves_the_tail_by_a_few_percent`). So
where the shipped model runs above the fitted curve, metabolism could account
for about an eighth of the excess where the excess is widest. That is 2.8 of
the 20.4 points at four hours, and 3.0 of the 24.0 points at 23.5 hours. Where
the shipped model runs below the fitted curve, metabolism widens the gap by the
same few percent. The reason is where the sink looks. Hepatic clearance sees
the arterial partial pressure, which through the tail is the alveolar one, and
it never sees the stores that feed it. The model's own conservation identity is
checked across the removals. The removals are recorded as exhausted agent, so
that § "Mass-balance identity" remains true with the sink in place.
<!-- not-restated: 5 %, 5.0 %, 1.3, 1.8 % -->

**What a learner sees of it: nothing on screen, and the record gains the
number.** The departures above are in $`F_A/F_{A0}`$. At the 1% dial of these runs,
$`F_{A0}`$ is 0.805, 0.672 and 0.876% of an atmosphere for sevoflurane,
isoflurane and desflurane. So the shipped alveolar trace falls below the
readouts' 0.01 percentage points (`docs/INTERFACE.md` § "Displayed precision") at 2.8, 4.2 and 1.9
hours. That is before the stretch over which the trace runs below the measured
mean. On the chart's linear axis, which is fixed at 3 MAC, the trace is a few
pixels high well before that. A higher dial scales $`F_{A0}`$ with it, and
keeps the trace above the 0.01 percentage-point limit for longer. A 6%
desflurane dial keeps it there until about the fifth hour, which is inside
desflurane's stretch. So a learner who runs a case long can reach the
shortfall.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

**The result does not bear on `docs/INTERFACE.md` § "Supported run length"**, which gives the full reasoning. The
departures computed here come from the missing fourth compartment and from the fat group's own
size, and both are present from the first hour to the last.

The checks are in
`tests/reference/test_late_washout_against_published_fits.py`. With these numbers,
`docs/MODEL.md` § "Intertissue diffusion: the missing fourth compartment" and
`docs/INTERFACE.md` § "Supported run length" can give a number as well as a direction. The coefficients were read at the source on 2026-09-27:
*Anesth Analg* p. 321 through the private corpus's text layer, and *Anesthesiology* pp. 494-95
as page images. `test_the_published_coefficients_sum_below_one_at_discontinuation` checks
their sum. The model runs in steps of 1 s, sampled once a minute.
`test_the_run_ends_at_the_supported_run_length` checks the run's length, and
`test_the_twenty_four_hour_run_opens_from_the_five_minute_gate_s_own_ratio` checks that its
fifth minute matches the ratios that the elimination regression pins hold, to four decimal places. The model's terms are the
exponential modes of its open-circuit system, decomposed from its state at discontinuation.
`test_the_model_s_apparent_muscle_and_fat_terms_against_the_fitted_ones` checks them. A test
requires the modes to match the stepped open-circuit run to within 0.08% at every minute from
the fifth. The difference is at most 0.0005% from the fifth minute on (from a run on
2026-11-21). The
run lies above the modes by the amount that the driver re-breathes within each step before it
empties the circuit. `test_the_muscle_group_s_slow_return_places_the_tail_s_rise_in_hours_2_to_4`
checks the result of lowering the muscle group's coefficient.
<!-- provenance: core/simulation_step.py SIMULATION_STEP_S = 1 -->

### Mass-balance test

Long wash-in, steady-delivery, and washout simulations must satisfy either
condition below. These are the run-time thresholds that § "Mass-balance
identity" gives, and the relative residual must also stay within that
section's mass-balance tolerance:

$$
|\varepsilon_M|
\leq
\varepsilon_{\mathrm{absolute,max}}
$$

or:

$$
\varepsilon_{\mathrm{relative}}
\leq
\varepsilon_{\mathrm{relative,max}}
$$

A sevoflurane test enforces these conditions
(`test_long_wash_in_and_washout_validate_agent_simulation` in
`tests/reference/test_sevo_patient.py`). A second test applies them to
isoflurane and desflurane (`test_wash_in_and_washout_validates_agent_simulation`
in `tests/reference/test_multi_agent.py`).

### Prediction agreement test

A preview predicts the seconds a run has not reached, in one-second steps from
the state the run stored at the second it has reached. The prediction must agree
with a run that stepped the same seconds to within rounding, at every second and
in every compartment. The run reads each fraction back from the amount of agent
in its compartment, and the prediction carries the fractions directly, so the two
routes are not the same arithmetic and agreement is evidence that both solve the
same equations.

The allowed difference is twice the summed rounding bound of the steps taken
(§ "How far a computed value can be from the exact one"), because each route lies
within that bound of the exact solution. That limit is far smaller than the
second decimal place of a displayed percentage (`docs/INTERFACE.md` § "Displayed
precision"). A prediction that stepped by any other length, or that was off by
one second, fails it.

The test is
`test_each_predicted_second_matches_the_second_the_run_stepped` in
`tests/unit/test_prediction.py`. `tests/unit/test_generated_runs.py` also holds
each prediction to the exact solution worked out to 50 digits. Other tests
compare stepped runs in two more cases: a system resumed at a stored state and
stepped from there, and a branch compared against its parent
(`tests/unit/test_resume_at.py` and
`tests/integration/controller/test_controller_branching.py`).

### Parameter-recovery test

The model must return a stored value, such as the alveolar volume, when this
test simulates a procedure that measures that value. Each procedure is derived
from a physical law, not from the equations in `docs/MODEL.md`. Like the other
verification tests, this test checks that the equations are the ones intended.
It cannot show that a stored value is right, because each procedure recovers
whatever value the data files hold.

**This test catches a class of error that the other verification tests miss.**
The test in § "Independent-solution test" solves the equations as written in
`docs/MODEL.md`, so it reproduces any error in them and still agrees with the
code. The test in § "Mass-balance test" catches an error only when agent is lost
or created. Suppose `docs/MODEL.md` gave the tissue capacity as $`V_i\lambda_{i:b}`$,
leaving out the blood:gas factor $`\lambda_{b:g}`$, and used that capacity in the
tissue's rate equation. Agent would still be conserved, and the independent
solution would agree with the code. The tissue volume recovered by the Fick
principle would be the stored volume divided by $`\lambda_{b:g}`$.

The test runs two procedures for each of the three agents. The first recovers
the alveolar volume by closed-circuit dilution. Lerou and Booij checked their
own system model by simulating this measurement with helium (Lerou JG, Booij LH.
Model-based administration of inhalation anaesthesia. 1. Developing a system
model. *Br J Anaesth* 2001;86:12–28, doi:10.1093/bja/86.1.12; PMID 11575385;
read at full text on 2026-09-06, and checked at the abstract through PubMed on
2026-10-25). The circuit fills
while ventilation is stopped. Setting the fresh gas flow to zero then closes the
circuit, and the lungs are ventilated from it with the cardiac output at zero.
With no blood flow, the agent behaves as an insoluble tracer, like helium in the
real measurement. Conservation then gives $`V_A = V_C(F_1-F_2)/F_2`$, where
$`F_1`$ is the circuit's fraction when it is closed and $`F_2`$ is the fraction
that the circuit and lungs share once they have mixed.

The first procedure is not the closed-circuit technique that `docs/MODEL.md` § "Low flow and the
closed circuit" says this model does not represent. That technique needs fresh gas
matched to the patient's uptake. The procedure has no fresh gas and, at zero
cardiac output, no uptake.

The second procedure recovers each tissue group's volume from its uptake over
the initial wash-in. It adds up the uptake that the Fick principle gives,
$`\dot U_i = Q_i\lambda_{b:g}(F_a-F_i)`$. It then divides the total by the
amount of agent that one litre of the tissue holds at the end of the run,
$`\lambda_{i:g}F_i`$, where $`F_i`$ is the tissue's own fraction.

The tests for the two procedures are
`test_an_alveolar_volume_recovered_by_closed_circuit_dilution_matches_the_stored_value`
and `test_a_tissue_volume_recovered_from_its_washin_matches_the_stored_value`,
in `tests/reference/test_parameter_recovery.py`. Both tolerances are relative. The
dilution's is at the level of rounding. The wash-in's is set by the error of
the test's own integration of the uptake, which applies Boole's rule to samples
one second apart. The test module gives each
tolerance beside the difference between the recovered and stored values from a
run of the test.

### Deterministic replay test

When two runs have the same initial state, parameters, setting changes, order
of events and simulation steps, they must produce identical results over the
whole run. Agreement within a tolerance is not enough. A run branched from
another must be identical to it at every instant the two share.

The results must not depend on how the run was paced in real time, as
§ "The reproducibility guarantee" states. They must be the same at every
playback rate that the interface offers.

The two runs' snapshots must match in every field, and each
segment and keyframe of one run's definition must equal the matching one in the
other's. Comparing only the end values would pass two runs that diverged and
then came back together.

To vary the pacing, one run takes one step per tick and the other takes its
steps in uneven bursts. Between ticks, the interface reads one run more often
than the other. Pacing both runs the same way would test one trajectory twice,
so it could not show that pacing has no effect.

A playback rate paces a run in bursts of steps. One test takes its rates from
the interface's own list, so a rate added to that list is tested from the day it
is added.

The tests for this section are
`test_identical_runs_produce_identical_snapshots`,
`test_a_run_reaches_the_same_definition_however_the_ticks_fell` and
`test_a_run_reaches_the_same_definition_at_every_playback_rate`, in
`tests/integration/test_sevo_controller.py`.

### Stored-state test

A run must give the same states whether or not they are read while it runs. Each
second's state is stored once, by the step that reached it, and every reader takes
that state (`docs/INTERFACE.md` § "Each second has one stored state"). A branch
holds its parent's stored states up to the fork and must repeat its parent's later
states in every digit while no setting differs.

The tests are in
`tests/integration/controller/test_controller_stored_states.py`. A branch with no
setting moved repeats its trunk's later states in every number
(`test_a_branch_with_no_setting_moved_repeats_its_trunks_later_states_in_every_number`),
which is what `ROADMAP.md` item 12 asks for.

## Release gate

A release is complete only when:

- all parameter values and sources are present;
- no scientific `TBD` markers remain;
- the model passes every check of the published-data gate, for every agent and
  cohort, the sign of the elimination disagreement included (§ "What the
  published-data gate can and cannot resolve" lists the checks);
- mass balance closes within the mass-balance tolerance (§ "Mass-balance
  identity");
- deterministic replay passes (§ "Deterministic replay test");
- changing a setting during a case keeps the simulation's current state;
- the interface contains the educational and non-clinical warning; and
- `docs/MODEL.md`, `docs/INTERFACE.md` and this document describe the behavior
  actually present in the tagged release.

The elimination regression pins compare simulated elimination with the model's
own earlier output. They run with the test suite, so a failing pin still stops
a release, but they are not among the published-data checks above. They check
only that the results have not changed, and do not show that they agree with
published data.

A release also needs these checks to pass:

- the circuit reference tests from v0.0.2;
- the unit, integration, invariant and independent reference tests;
- the tests of § "Step-refinement test", and the nonnegativity tests;
- Ruff formatting and linting;
- strict mypy;
- pytest; and
- GitHub Actions.

The five-minute elimination pin is in the same test module as the
published-data gate. The late-washout tables are in a test module of their own.

## Notes for developers on the model description

`docs/MODEL.md` describes the model for a clinician or educator. This section
holds what a developer needs beside it: where each part of the model is in
the code, the rules the code must keep, and the tests behind its statements.
Each subsection follows the part of `docs/MODEL.md` it serves.

### What keeps a real patient's data out of a run

Using this simulator outside the intended use in `docs/MODEL.md` § "What the simulator is for" is **reasonably foreseeable
misuse** under ISO 14971:2019, the risk-management standard for medical devices.
Its clause 5.2 requires documenting such misuse. The hazard table
(§ "Reasonably foreseeable misuse, and the hazards the presentation carries")
has a row for it.

Two safeguards protect against this misuse today:

1. The use statement at the foot of the window says that the simulator is for
   teaching and is not a clinical prediction, monitoring or dosing tool. In
   each built-in Workspace it stays in view, however the page scrolls.
2. The simulated patient is always the same reference adult. No control accepts
   a weight, age, sex, height or body composition. Every run keeps that
   patient's compartment volumes and perfusion fractions, whatever the learner
   sets. The planned patient factors (`ROADMAP.md` planned-milestone item 30)
   will remove this safeguard.

A learner can still set cardiac output or alveolar ventilation to a value
measured in a real patient, because changing them is a core teaching feature.
The run then shows the reference adult at that flow, not a prediction for that
patient. Only the use statement guards against reading the run as one.

The use statement is `USE_DISCLAIMER_TEXT` in `app/dashboard_frame.py`,
and the reference adult is stored in `data/patients/reference_adult.json`. A test checks each
way a patient could get into a run today, so adding patient factors will make it fail
(`test_every_run_simulates_the_shipped_reference_adult`). The change that adds them must then
rewrite this section and the hazard table's row for a real patient's data.

### Software safety classification: Class C, for the whole application

This project assigns **Class C to the whole application**, the interface
included. IEC 62304 § 4.3 classifies software by the severity of the harm that
its failure could contribute to. **Class A** applies where no injury or damage
to health is possible, **Class B** where injury is possible but not serious, and
**Class C** where death or serious injury is possible. The class depends on
severity alone (Annex B.4.3). Where software sits in a sequence of events
leading to a hazardous situation, the standard sets the probability of its failure to 1, rather than estimating it. So an argument that a failure would rarely happen does not justify a lower class.

A failure of the interface could contribute to injury, which rules out Class A.
A correct number is still a safety failure if the interface shows it with the
wrong units, label, patient context or model version, or after it has gone out
of date. The interface also has safety features, such as the distinction
between a halted and a paused run, the rule on displayed precision and the
ISO 5360 agent colours.

A lower class for any part of the application would save no
work, because this project checks all its code the same way. Class A, for
example, excuses software from detailed design, unit verification and
integration testing.

Code that looks cosmetic cannot be split off into a lower class, because it
carries clinical meaning. The chart's frame (`app/chart_frame.py`) decides what
a chart line claims about a run. The styling file (`app/theme.py`) defines the
ISO 5360 agent colours. The rule for which instants the chart draws is a safety
feature of the interface. The chart computes the run's exact state at each
instant that it draws, and every control change is one of those instants
(`docs/INTERFACE.md` § "Interface boundary").

A split would pay off only where the exempted part is large, genuinely
non-clinical and costly to verify. None of those holds now.

### Class C is an engineering bar, not a regulatory status

The project adopts Class C for the whole application as an engineering standard,
like WCAG 2.2 AA for accessibility (`docs/INTERFACE.md` § "Color contrast, and the standard this
interface is held to"). The project claims no conformance to IEC 62304 or to a
quality management system, and no regulatory status. Writing the class down gives
anyone reviewing the code a bar to hold it to.

The class does not settle whether the simulator is a medical device. FDA
publishes examples of software functions that are *not* medical devices. They
include software intended for health care professionals as educational tools
for medical training. One example is "games that simulate various cardiac
arrest scenarios to train health professionals in advanced cardiopulmonary
resuscitation (CPR) skills" ([FDA, Examples of Software
Functions That Are NOT Medical Devices](https://www.fda.gov/medical-devices/device-software-functions-including-mobile-medical-applications/examples-software-functions-are-not-medical-devices),
and the guidance "Policy for Device Software Functions and Mobile Medical
Applications"). Whether software is excluded depends on its intended use, not
on which physiologic parameters it accepts. To qualify, the software must not
support a health professional's assessment of a *specific patient*. That is why
the intended-use boundary in `docs/MODEL.md` § "What the simulator is for" is drawn at a specific patient's data.

Before you revise this section, the one before it, or the paragraph on misuse
in § "What keeps a real patient's data out of a run", check IEC 62304 and
ISO 14971 directly. They are not open access, so the project read their clause structure,
the three class definitions and Annex B.4.3's probability rule from secondary
summaries. The Class C conclusion does not depend on the standards' wording, but
the clause numbers cited here do. The project read the FDA material at the source.

### The model boundary in the code

Before extending the model to a multi-limb system, record
the change in `docs/MODEL.md` § "What the model represents". Such a system separates inspired gas from mean
circuit gas, as Lerou and Booij's three-part model does. The two would then be
tracked separately, and this model's single $`F_I`$ would no longer describe
both.

### Assumptions in the code

The vaporizer control is `ControlInput.DELIVERED` in
`app/control_record.py`. Each recorded change to it carries the unit *percent
of 1 atm*. The model has no parameter for the class of vaporizer and needs none
at sea level. A model that adds ambient pressure will need one.

### Time

Times are in seconds in the equations, the model's code and a saved run.
The model keeps its own simulation time and never takes it from the computer's
clock. That clock may still decide when the screen updates.

A run stores each flow as it was set, in liters per minute
(`UptakeEquationSettings` in `core/governing_equations.py`). Each time the
equations need a flow, the model converts it to liters per second:

$$
\dot V_{\mathrm{s}} = \frac{\dot V_{\mathrm{min}}}{60}
$$

The per-second value of each flow is never stored because
multiplying it by 60 can give a number that differs from the setting. On a
0.1 L/min grid across the supported 0 to 10 L/min range, the round trip fails
for 7 of the 101 cardiac outputs (1.9, 3.8, 3.9 and 7.6 to 7.9 L/min). The
tissue flows formed from cardiac output share that difference. Settings rebuilt
from per-second values could therefore describe a run that nobody set up.
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->

#### Simulated time is a count of steps, not a running total

A run moves forward in steps of 1 s, and it takes no step of any other
length. Simulated time is the number of steps the run has completed, so it is
always a whole number of seconds. A computer holds a whole number exactly. So
no instant of a run is a rounded value, and two instants can be compared
exactly.
<!-- provenance: core/simulation_step.py SIMULATION_STEP_S = 1 -->

A run's settings change only between two steps. So a control change takes
effect at the next whole second, and the run records it at that second.
§ "Supported simulation step" gives what that delay can cost a displayed value.

The model stores the count of completed steps
(`SimulationState.step_count`) and returns it as the simulated time
(`SimulationState.elapsed_s`), a whole number of seconds. A branched run
continues the count of the run it branched from. So its time is still one
count, and is not the instant of the branch plus a second total. Reset sets the
count to zero.

#### The reproducibility guarantee

Two runs with the same inputs are **exactly identical** in every stored value at
any step *n*, which falls at *n* seconds in both. Those inputs are the
starting state, parameters, setting changes and order of events.
Every comparison of one run with another relies on the guarantee. That includes
comparing a branched run with the run it branched from, at every instant they
share. `docs/INTERFACE.md` § "What a branch comparison asserts, and what it does not" says what such
a comparison may and may not claim.

**A slow or busy computer reaches each step later in real time, but computes and
stores the same values as a fast one.** The screen uses the computer's clock to
decide when to update. But the number of steps in each update follows from the
playback rate the user chooses, and is never measured from the clock. The simulation never takes
extra steps to catch up after a slow update, and it reads no clock. An automatic
check keeps the model's code from reading the clock, and from drawing a random
number that differs from run to run.

**Playing a run faster does not make it a different run.** The playback rate is
how much simulated time passes per second of real time. A faster rate takes
more *whole steps* per second of real time, never a larger step. So a case played at
real time and at three hundred times real time takes the same steps, in the
same order, at the same size, and gives exactly the same results sooner.

The guarantee does not cover three things, and none of them is a defect:

- **A different model version.** The guarantee applies within one version of
  the equations and one parameter set. That is why both are versioned.
- **A different installation.** Basic arithmetic gives identical results on
  every computer. But each step also uses an exponential function, whose last
  digit can differ from one installation of the simulator to another.
- **Elapsed real time.** How long a computer takes to reach step *n* is a
  property of the computer. So is how many steps it has reached when a
  wall-clock minute is up. Neither is a property of the model.

**Every value shown, compared or branched from is a state the run stored.** A run
stores the state that each step wrote, one for each second it reaches, and every
reader of a reached second takes that state rather than computing it again
(`docs/INTERFACE.md` § "Each second has one stored state"). So two readers of one
second get exactly the same bits. The one computed state is a preview of a setting
not yet applied, which is only drawn.

Faster playback never enlarges the step, because a larger
step would compute a second solution of the same equations, one that the
guarantee does not cover. A displayed value would then depend on how fast the
user was watching, and no label could fix that.

The check on the model's code is `tools/import_boundary_check.py`. It runs in
`make check` and CI, and it fails the build when any module under
`src/anesthesia_sim/core/` imports `time`, `datetime`, `random`, `secrets` or
`uuid`. If it missed any of these imports, a run could stop being reproducible
while the check still passed. The check stops at `core/` so that the screen
code outside it may use the clock. A table in the check (`BOUNDARIES`) gives
the reason for each entry.

Seeding cannot make `secrets` or `uuid` repeatable. Python's `secrets` module
draws from `random.SystemRandom`, whose `seed()` is documented to do nothing
and whose `getstate()` raises an error. The function `uuid.uuid1()` mixes the
current time with the host's hardware address, so a run that used it would
differ between *machines* as well as between runs.

The exponential in each step is one `exp()` call, a library function whose last
bit can differ between platforms, Python builds and math libraries. The
propagator is also built from a series and a sequence of squarings, and a
compiler may change the order in which their terms are summed.

### Concentrations

Every concentration that the model computes is a dimensionless
partial-pressure-equivalent fraction.

The vaporizer dial and MAC are given in percent of an atmosphere. The
conversion between a fraction and a percent is:

$$
\text{percent} = 100F
$$

For example, $`F = 0.02`$ represents a 2% gas-phase concentration
(`test_the_two_forms_convert_both_ways`).

The conversion has only two uses. Where the equations need $`F_D`$, the model
derives it from the dial's percent. The screen converts for display. The model
treats a fraction and a percent as different kinds of number, and rejects one
where the other is wanted.

**The vaporizer setting is stored as the percent dialled.** It is the only
concentration that is set rather than computed. Converting a fraction back to a
percent does not always return the setting, so a value kept as a fraction could
not give back what a learner dialled. A new run starts the dial at the agent's
published percent, without converting it. An error message about a setting
gives it in percent, beside the vaporizer maximum, which is also stored in
percent. Like the vaporizer setting, the flows are stored as set (§ "Time").

**A concentration's range is checked once, when the concentration is created.**
A fraction must always be finite and satisfy:

$$
0 \leq F \leq 1
$$

A percent must be finite and lie from 0 to 100. Every place that stores a
concentration accepts only a checked value.

Each fraction computed in a step is checked before a compartment stores it, in
`AgentUptakeSystem._write_state_vector`. A value outside 0 through 1 halts the
run and names the compartment, instead of being stored or shown. Supported
settings never lead to such a value. The delivered concentration and each
starting fraction must be at or below 0.99 of ambient pressure
(§ "The numerical envelope"), because rounding can carry a step's result a
little above the largest fraction that the step started from. The figures
behind the 0.99 limit are recorded in `core/concentration.py`.
<!-- provenance: core/supported_ranges.py MAXIMUM_INPUT_FRACTION = 0.99 -->

The conversion between a fraction and a percent is written
only in `src/anesthesia_sim/core/concentration.py`, in both directions. The two
forms are distinct types there, `Fraction` and `Percent`, so a type checker
rejects a percent where a fraction is wanted before the program runs. When the
program runs, a value of the wrong form is rejected as a missed conversion
rather than as a value out of range. The code also rejects a value that is
already converted, or one that does not say which form it is in.

The breathing circuit stores the dial's percent, and so do the record of control
changes and the settings that a run records for each stretch. The model derives
$`F_D`$ from that percent in both the circuit and the recorded settings. A new
run's dial is set in `AgentUptakeSystem.for_agent()`.

On a 0 to 8% dial in 0.01% steps, multiplying a fraction by 100 fails to return
the percent it came from for 126 of the 801 settings. The first failure is at
0.23%, and 0.9% comes back as 0.9000000000000001
(`test_a_round_trip_through_a_fraction_misses_the_dialled_percent_at_126_of_801_positions`).
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->

The agent's MAC is stored as a `MacPercent`, a `Percent` that rejects zero when
it is built. Every formatter that computes a MAC multiple accepts only that
kind of percent as its divisor. No other lower limit is set on the MAC, so a MAC
far below any real agent's would still give multiples too large to read. The
shipped MACs at age 40 are 1.17% to 6.6%.
<!-- provenance: data/agents/isoflurane.json mac_at_age_40_percent = 1.17 -->
<!-- provenance: data/agents/desflurane.json mac_at_age_40_percent = 6.6 -->

The rules that the fraction and percent types share with the flows are written
once, in `core/checked_number.py` (`docs/INTERFACE.md` § "Supported input ranges"): what counts as a
number, that one checked quantity is never created from another, and that minus
zero is stored as zero.

The places that store a concentration are these:

- each compartment's setter
- the driving fraction that a compartment's own closed form takes
- the breathing circuit, when it is built or set (`BreathingCircuit`)
- the saved state that a rollback restores the circuit from
  (`BreathingCircuitState`)
- the settings that a run is built from (`UptakeEquationSettings`)
- the parameters that an agent's data file is parsed into, which hold its MAC
  and vaporizer maximum (`AgentParameters`)

### Symbols

The **Code** column names the one place in the model's code that holds each
symbol.

Each Code cell is written `ClassName.accessor`. Where a
symbol has no place of its own in the code, its Code cell shows an em dash
followed by what the code reads instead. $`\Delta t`$ and $`F_a`$ are the only such symbols.

A reader who knows the model's symbols should be able to follow the code
without the Code column, so code that needs the column to be understood has a
defect.

| Symbol | Meaning | Unit | Code |
| --- | --- | --- | --- |
| $`t`$ | Elapsed simulation time | s | `SimulationState.elapsed_s` |
| $`\Delta t`$ | An interval of simulated time. A run's step is one second (§ "Supported simulation step") | s | — the code reads the constant `SIMULATION_STEP_S` for a run's step; a compartment stepped on its own takes its interval as an argument |
| $`F_D`$ | Delivered fresh-gas agent fraction | dimensionless | `BreathingCircuit.delivered_partial_pressure_fraction` |
| $`F_I`$ | Inspired agent fraction, taken as the fraction in the breathing circuit (`docs/MODEL.md` § "What the model represents" states the assumption that makes circuit gas and inspired gas one quantity, and what would break it) | dimensionless | `BreathingCircuit.inspired_partial_pressure_fraction` |
| $`F_A`$ | Alveolar agent fraction | dimensionless | `AlveolarCompartment.partial_pressure_fraction` |
| $`F_a`$ | Arterial partial-pressure-equivalent fraction, defined as $`F_a \equiv F_A`$ (`docs/MODEL.md` § "What the model represents") | dimensionless | — the code reads `AlveolarCompartment.partial_pressure_fraction` wherever an arterial fraction is required |
| $`F_v`$ | Venous blood partial-pressure-equivalent fraction | dimensionless | `VenousBloodCompartment.partial_pressure_fraction` |
| $`F_i`$ | Tissue group $`i`$ partial-pressure-equivalent fraction | dimensionless | `TissueGroup.partial_pressure_fraction` |
| $`V_C`$ | Mixed breathing-circuit volume | L gas | `BreathingCircuit.circuit_volume_l` |
| $`V_A`$ | Modeled alveolar gas volume | L gas | `AlveolarCompartment.gas_volume_l` |
| $`V_v`$ | Venous blood-pool volume | L blood | `VenousBloodCompartment.volume_l` |
| $`V_i`$ | Volume of tissue group $`i`$ | L tissue | `TissueGroup.volume_l` |
| $`\dot V_F`$ | Fresh gas flow at the common gas outlet: carrier gas plus the vapour the vaporizer added, not the flowmeter setting (see `docs/MODEL.md` § "Breathing circuit") | L gas/min | `BreathingCircuit.fresh_gas_flow_l_min` |
| $`\dot V_A`$ | Alveolar ventilation | L gas/min | `AlveolarCompartment.alveolar_ventilation_l_min` |
| $`Q`$ | Cardiac output | L blood/min | `PatientCompartments.cardiac_output_l_min` |
| $`Q_i`$ | Blood flow to tissue group $`i`$, formed as $`f_iQ`$ and never stored | L blood/min | `TissueGroup.blood_flow_l_min_at` |
| $`f_i`$ | Fraction of cardiac output reaching tissue group $`i`$ | dimensionless | `TissueGroup.perfusion_fraction` |
| $`\mathrm{MAC}_\%`$ | The agent's alveolar concentration at 1 MAC for a 40-year-old, from Mapleson's 1996 meta-analysis. It sets the dial's starting position and is the divisor for the display in MAC multiples. No governing equation reads it | percent | `AgentParameters.mac_at_age_40_percent` |
| $`\lambda_{b:g}`$ | Agent blood:gas partition coefficient, read from the agent data files and stored once per patient in the venous pool | dimensionless | `PatientCompartments.blood_gas_partition_coefficient` |
| $`\lambda_{i:g}`$ | Tissue:gas partition coefficient for group $`i`$, read from the agent data files | dimensionless | `TissueGroup.tissue_gas_partition_coefficient` |
| $`\lambda_{i:b}`$ | Tissue:blood partition coefficient for group $`i`$, derived as $`\lambda_{i:g}/\lambda_{b:g}`$ and never stored | dimensionless | `TissueGroup.tissue_blood_partition_coefficient_for` |
| $`M_C`$ | Agent stored in the breathing circuit | L equivalent gas | `BreathingCircuit.agent_amount_l` |
| $`M_A`$ | Agent stored in alveolar gas | L equivalent gas | `AlveolarCompartment.agent_amount_l` |
| $`M_v`$ | Agent stored in venous blood | L equivalent gas | `VenousBloodCompartment.agent_amount_l` |
| $`M_i`$ | Agent stored in tissue group $`i`$ | L equivalent gas | `TissueGroup.agent_amount_l` |

The symbols for the two tissue coefficients name both phases in order, because
the primary literature has no convention that would let a reader supply a
missing phase. Baker and Farmery's 2011 review gives one quantity three names in
a single chapter: the tissue-gas partition coefficient (p. 569), the
tissue-blood partition coefficient (p. 570) and the blood tissue partition
coefficient (Table 2). The review's Eq. (4) shows that the quantity is the
tissue:blood coefficient. The full citation is in the reference list,
`docs/references/README.md`.

The code's names for the two tissue coefficients give both phases in order, as
their symbols do.

The gas-phase symbols follow the inhaled-anesthetic literature:
$`F_D \rightarrow F_I \rightarrow F_A`$. Symbols and the gas-phase cascade
($`F_D`$, $`F_I`$, $`F_A`$) follow Hendrickx and De Wolf (2008, pp. 161-162).
They attribute the $`F_D - F_I`$ gradient to rebreathing (p. 169) and the
$`F_I - F_A`$ gradient to uptake (p. 171), and describe the teaching role of
the $`F_A/F_I`$ curve (p. 167). The chapter's full citation is in the reference
list, `docs/references/README.md`
§ "Schüttler & Schwilden 2008 — *Modern Anesthetics*".

**The symbols for inspired and tissue fractions differ only in case.** $`F_I`$
is the inspired fraction, and $`F_i`$ is tissue group $`i`$'s fraction. Where
both appear in one expression, the tissue index is written out.

The case-only difference between $`F_I`$ and $`F_i`$ stays because both are
standard in the literature. Renaming either would make this model's symbols
disagree with every source a reader is likely to come from.

### Tissue groups and compartment capacities in the code

In the code, the tolerance on $`\sum_i f_i = 1`$ is
`FLOW_FRACTION_TOLERANCE = 1e-12`, defined in `core/rounding.py`.

When the model sets up the patient's compartments
(`PatientCompartments.from_parameters`), it writes the blood:gas coefficient
once, into the venous pool, and the tissue groups store none. The pool refuses a second value,
and the patient refuses a replacement pool with a different one. If each tissue
group kept its own copy, the copies could disagree and no check would fire. A
pool at 0.1 beside groups at sevoflurane's 0.65 would still conserve agent, and
the run would give uptake curves that look plausible and are wrong.
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->

The code computes the capacity from the tissue:gas
coefficient, in one multiplication (`TissueGroup.capacity_l`). The code takes
the blood:gas coefficient from the venous pool
(`PatientCompartments.blood_gas_partition_coefficient`) for the lung's uptake
term and for each tissue group's tissue:blood coefficient.

### The breathing circuit in the code

The tests from v0.0.2 that check the equation for the
circuit alone against its exact solution are in § "Preserved circuit reference
tests".

Desflurane's dial maximum is stored in `data/agents/desflurane.json` as
`max_delivered_concentration_percent`.

A machine's $`V_C`$ is stored as `circuit_volume_l` in its file in
`data/machines/`. It holds the assembled total of apparatus and patient circuit
until the split planned in `docs/machine-abstraction.md` stores the apparatus
volume separately, as `apparatus_volume_l`.

An apparatus figure stored alone shortens the circuit time constant by the
patient circuit's share. At 4.0 L/min, a Perseus A500's 2.1 L apparatus volume
gives a time constant of 31.5 s, 36% shorter than the 49.5 s from its assembled
3.3 L. No automatic check can catch that error, because both are correctly cited
volumes (§ "How this document is held to the tree" says what the documentation
check confirms).
<!-- derived: 31.5 s from data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4.0 -->
<!-- derived: 49.5 s from data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4.0 -->

Closed-circuit operation needs both a variable alveolar volume and a patient who
consumes oxygen, so it is not among the three entries in `docs/MODEL.md` § "Nitrous oxide and the fixed alveolar volume"
that come from the fixed alveolar volume alone.

Setting only the exhaust's removal rate to zero does not model a closed circuit.
The changed model runs without error and gives a plausible curve. Its circuit
settles at $`F_I = F_A + \dot V_FF_D/\dot V_A`$.
At the opening fresh gas flow of 4.0 L/min, with the reference adult's 4 L/min
alveolar ventilation and a 2% dial, that is two percentage points above
alveolar. In the steady state every litre of delivered agent reaches the
patient, as in a closed circuit, but nothing ties the fresh gas flow to uptake.
At 4.0 L/min and the same dial, the vaporizer adds agent about thirteen times
faster than at the 0.3 L/min that this patient's uptake would set.
<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->

Closed-circuit operation is a property of the machine, and one coefficient
switched by a condition is the wrong way to model it. The machine design in
`docs/machine-abstraction.md` reserves a place for it, a removal strategy named
`closed_circuit`, recorded there as not implemented.

### The alveolar gas equation in the code

With the delivered fraction set to zero, the six equations
become $`d\mathbf{F}/dt = A_6\mathbf{F}`$. $`A_6`$ is the 6×6 block of the
matrix of the model's equations (`build_system_matrix` in
`core/governing_equations.py`), in that module's state order. Each of the six
exponential terms is $`e^{\lambda_k t}`$ for one eigenvalue $`\lambda_k`$ of
$`A_6`$, with time constant $`\tau_k = -1/\operatorname{Re}\lambda_k`$. The
5.83 s figure comes from a search over a grid of 11 fresh gas flows, 13
ventilations and 21 cardiac outputs for each agent, refined along cardiac
output. The fastest point is isoflurane's at the largest fresh gas flow and
ventilation, and the refined cardiac output is 9.325 L/min. The time constant
there differs from its value at 9.32 or 9.33 L/min by less than 0.00001 s, so
`docs/MODEL.md` gives the cardiac output as about 9.3 L/min.
`test_the_fastest_time_constant_is_the_one_the_model_document_prints` in
`tests/unit/test_governing_equations.py` repeats the search on the shipped
system matrix and holds both figures to the ones `docs/MODEL.md` prints.

Many numerical methods need steps short compared with the fastest time constant
to keep their errors from growing. The slowest time constant is about 5 700 to
14 900 times the fastest, so these methods would take many steps over a run
long enough for the slowest to matter. The exact method of
§ "Selected method (as implemented)" does not need such short steps.

The test that recomputes the table is
`test_modal_time_constants_are_the_pinned_ones` in
`tests/reference/test_coupled_dynamics.py`. That file holds the test's own copy
of the equations. When the test fails, its message says to re-derive the table.
On 2026-11-01, the eigenvalues of the matrix of the model's equations agreed
with the table's figures, and with the values from the test's copy, to within a
relative difference of 3e-15.

In the matrix of the model's equations, the alveolar row divides each of its
terms by the alveolar volume (`alveolar_volume_l`), which the equation settings
hold fixed for the whole step. Two standard formulations lift the fixed-volume
constraint, and a milestone that adds several gases could adopt either one. They
are equivalent to first order. The first lets $`V_A`$ change over time, and the
concentration equation gains a volume term:

$$
\frac{dV_A}{dt} = \dot V_{A,\mathrm{in}} - \dot V_{A,\mathrm{out}} - \sum_k \dot M_{\mathrm{uptake},k}
\qquad
\frac{dF_A}{dt} = \frac{dM_A/dt - F_A\,dV_A/dt}{V_A}
$$

The second keeps $`V_A`$ constant and replaces the volume lost to total uptake
with inspired gas, so the effective inspired ventilation becomes
$`\dot V_A + \sum_k \dot M_{\mathrm{uptake},k}`$. This formulation is the
smaller change to the model, and the one that the classical treatment uses.

Either way, the second-gas effect follows from the alveolus holding more than
one gas, and needs no machinery of its own. Because the gases are coupled
through the alveolar volume, the roadmap says to model the patient as a set of
substances instead of bolting nitrous oxide on beside a volatile agent
(`ROADMAP.md` planned item 6). A patient model built that way makes planned
item 7 nearly free. Bolting nitrous oxide on instead would leave item 7
unreachable.

Nitrous oxide's blood:gas coefficient of 0.47, in the table in
`docs/MODEL.md` § "Nitrous oxide and the fixed alveolar volume", is not stored.
Adopting it would need an entry of its own that
meets the standard set in `docs/PARAMETERS.md` § "Source hierarchy".

### Tissue uptake in the code

A blood flow can be above zero and still so small that $`\tau_i`$ is larger
than any number the computer can hold. Then the method that computes $`\tau_i`$
(`TissueGroup.time_constant_s`) returns infinity, as it does at zero flow, and a tissue group
stepped on its own is left unchanged. The exact change in the agent it holds is far smaller than
any amount the simulator displays. A test in `tests/unit/test_blood_flow.py` checks this at the
smallest flow that can be created. The venous pool's time constant
(`VenousBloodCompartment.time_constant_s`) is infinite in the same way at a cardiac output that
small, and a second test there checks it.

## How this document is held to the tree

The first subsection below gives the rules that a reader of this document
relies on. The second gives the rest, for the people who write it.

### What a named test, a missing test and a date tell the reader

When a statement in this document, in `docs/PARAMETERS.md` or in `README.md`
is about the simulator's code, data or output, it names the thing it describes. Where no test covers the
statement yet, it says so in a fixed form, ``no test yet (`PL-XXXX`)``, and the
parenthesis names the open work item for adding the test.

Each name is set in fixed-width type and points to a test, a file, or a part of
the code or its data. A number repeated from the simulator's data is linked to
the stored value. An automatic documentation check looks up each name and link.
Without that check, a sentence would still read as true after the test it names
was renamed, the data it describes was removed or the value it repeats was
changed.

When a statement carries a date, sits under a dated heading or sits in a
released version's section, it records what was true on that date. It need not
name a test, and nothing checks it against the code. A later fact gets its own
date, and the dated statement is never changed to carry it.

`docs/MODEL.md` is written for a clinician and names no test. Where a test
holds one of its statements, this document or `docs/PARAMETERS.md` names it.

### What the documentation check confirms, and what only a review finds

For a figure that the model computes or the simulator displays, such as the time
at which a compartment first shows a nonzero reading, the sentence that gives
the figure names the test that computes it, or uses the fixed form. Where that
test also reads the figure from this document and compares it with the model's
output, the document cannot drift from the model without the test failing.

In some parts of this document, an automatic check makes sure that each claim
names in fixed-width type what it describes. It checks every row of the hazard
table, every entry of the required invariants, every subsection of the required
tests, and every output in the displayed-outputs list of `docs/INTERFACE.md`.

In the sections that the check reads paragraph by paragraph, every number with a
unit has something behind it. Its paragraph gives a test, the fixed form, a date
or a published source, or links the number to the simulator's data.

Outside these lists and sections, only the documentation review before a work
item closes finds a number with nothing behind it, or a claim that does not name
what it describes. The review does the same for a qualitative claim, such as
which value a readout shows beside a halt, because the check cannot read one.

A count in this document is dated, checked against what it counts, or copied
from a tool that prints it. For example, a check compares the count in a heading
with the entries under it. Nothing checks a copied count later, so it can go out
of date.

These rules apply in part to the project's other
documents. The frozen lists in `ROADMAP.md` and the package map in
`docs/ARCHITECTURE.md` promise an entry for each member of a set, and each has
checks of its own. The check of a frozen list reads only the lines that open
with an item id. The prose of `ROADMAP.md` is treated as dated. Every thread in
`docs/WORKING_NOTES.md` is dated, so only the rule for dated statements applies
to it. The rules do not apply to prose about the project's workflow tooling, in
`.claude/`, `CONTRIBUTING.md` and `docs/resident-instructions.md`, where the
rule on counts is only advice.

The rule that a claim names what it describes also applies to two documents that
describe the code: to every paragraph of `docs/ARCHITECTURE.md`, and to every
paragraph of `docs/interface-provenance.md` § "What this project adopts, diverges
from, and refuses". Each such paragraph names in fixed-width type the module,
symbol or test it describes, or uses the fixed form ``no code yet (`PL-XXXX`)``.
An item id alone names no code. The documentation check reads both paragraph by
paragraph (`check_bound_families`). When something that a paragraph names
changes, the command for the documentation review
(`tools/doc_check.py candidates`) prints the paragraph's first and last line
(`PL-BLN0`).

A statement is about the code or its data when it says, for example, that a test
enforces a rule, that a field exists, that a value is *N*, or that a job runs
something. It names that thing as a test, path, symbol or field in fixed-width
type, or with a `<!-- provenance: -->` marker over a restated number. In the
documentation check (`tools/doc_check.py`), `check_named_tests` looks up a
test, `check_citations` a path, `check_prose_provenance` a marker and
`check_make_targets` a `make` command. No check looks up a symbol or a field. The strongest link for a figure from the model is a test
that reads it from the document that states it, as
`tests/reference/test_known_limitations_figures.py` does for
`docs/MODEL.md` § "Known limitations".

A writer may phrase the words before ``no test yet (`PL-XXXX`)`` freely, but the
form itself is fixed, so that the documentation check can tell a forgotten link
from a declared absence. Closing the named item without adding the link makes
the check fail.

The lists whose headings promise an entry for each member of a set are the
invariants list, the required-tests subsections, the displayed-outputs list, the
hazard table, a frozen gate list and a marked enumeration. The function that
checks them (`check_bound_families`) reads only the lists and sections named in
its table, each section paragraph by paragraph. A list or a section joins that
table only when the change that makes it conform is merged, so that work not
yet done never makes `make check` fail.

In those sections, a published source counts only when it is cited by a DOI, a
PubMed id, an ISBN or a journal locator such as "Anesth Analg 1991;72:316-324".
An author and a year alone, such as "Mapleson 1963", do not count, because no
pattern can tell them from a phrase such as "Until 2026".

A paragraph's test or fixed form may sit in the note for developers below it.
That note covers the paragraphs directly above it, back to the previous heading
or note, and stops at the first paragraph that has a test, the fixed form, a date or a
source of its own. A date or a
source in the note covers only the note.

A paragraph with no test, fixed form, date or source passes only if a marker
covers each number that it states with a unit. A `provenance:` marker covers a
value the paragraph states, in that value's unit. A `derived:` marker covers a
figure that the paragraph works out, in the unit it writes, and each input the
paragraph states. A `not-restated:` marker covers nothing, because it says that
the paragraph's numbers are not stored values. So a computed figure cannot pass
on a marker written for a figure beside it.

Outside the lists and sections where the check looks for a missing name, a
command for the documentation review (`tools/doc_check.py candidates`) prints
each line that names a file, a definition or a data key that a change touched.
Only the reviewer finds a number or a claim on a line that names none of these.

Besides a count in a heading, a check compares a count with what it counts only
through a marker over a data value. Any other count is dated, copied from a
tool, or left out. This document never states the number of entries in the
hazard table or in any other list named in this section. The function that
checks gate counts (`check_gate_counts`) applies the rule on counts in code. It
checks each count that a frozen list states about itself against the list: in a
group heading, in a release table, and in the sentence that says how many
entries are marked `not-delegable`. It refuses a count written into a lower
heading, which it cannot check. It leaves other counts in prose alone, because a
sentence such as "frozen at seventeen entries" records a dated fact that must
never change.

This section's rules follow requirements traceability, the established practice
for software of this application's safety class (§ "Software safety
classification: Class C, for the whole application"). Traceability links each
requirement to the tests and risk controls that cover it. IEC 62304 § 5.1.1
requires the software development plan to carry traceability between system
requirements, software requirements, software system tests and risk control
measures. The FDA's *General Principles of Software Validation* (2002) § 5.2.2
names traceability analysis among the validation tasks. Gotel and Finkelstein
set out the problem in *An analysis of the requirements traceability problem*,
ICRE 1994, pp. 94–101.
