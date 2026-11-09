# The anesthesia-machine abstraction: what a machine module is

## What this document is, and what it is not

A milestone planned in `ROADMAP.md` (planned-milestone item 1) commits to a
modular anesthesia-machine abstraction, so that **a real commercial machine can
be added as a module**. This document is the design for that abstraction. It
sets out what a module *is*, and answers the seven questions in its design brief
(`PL-FG9D`). A survey written for this design (`docs/machine-survey.md`) found
which differences between real machines affect a number this simulator computes.
The sections come in this order:

- § "A machine changes only two rates and one volume" gives the finding the
  whole design rests on.
- Question 3: how a machine composes with the existing core, that is, what the
  base owns and what each machine supplies.
- Question 1: where the parameter/strategy line falls.
- Question 2: what keeps the machine profile small.
- § "Which values belong to the machine, the run and the model".
- Question 4: validation and provenance per machine.
- § "Fresh gas inlet position is not modelled".
- Question 5: naming a real machine in the interface.
- Question 6: every difference between machines traces to a named field.
- Question 7: what the second machine costs.
- § "What this design does not decide" lists the open matters.

**Design only.** Nothing here changes `src/`. Building a machine class,
interlocks or a data migration is the milestone's work, and this design is what
lets the milestone be scoped. Where a decision below implies work, the work is
named and left to the milestone.

**Not held to the tree.** `docs/MODEL.md` specifies the model *as implemented*
and its § "How this document is held to the tree" binds every live assertion in
it to something a script can resolve. This design is not implemented, so
writing it into that document would put unresolvable assertions inside a bound
one. It sits beside `docs/machine-survey.md` for the same reason, and
`docs/MODEL.md` gains its statements when item 1 lands them.

## A machine changes only two rates and one volume

**A machine contributes exactly two rates and one volume** to the breathing
circuit's row of the system matrix, and nothing else anywhere in the model. The
two rates are the agent delivery rate $`\dot m_{\mathrm{in}}`$ and the circuit
gas removal rate $`\dot m_{\mathrm{out}}`$, both in L/s. The volume $`V_C`$ is
the space that the circuit gas occupies in the apparatus. Everything the survey
found falls under one of the three.

The model is one system matrix $`A`$ over nine states, built in
`src/anesthesia_sim/core/governing_equations.py`. Its exact propagator is
$`\exp(A\,\Delta t)`$. Five entries of that matrix belong to the breathing circuit.
The circuit's own row has three of them:

$$
A_{F_I,F_I} = -\frac{\dot V_F + \dot V_A}{V_C},\qquad
A_{F_I,F_A} = \frac{\dot V_A}{V_C},\qquad
A_{F_I,\mathbf 1} = \frac{\dot V_F F_D}{V_C}
$$

with two more in the accounting rows,
$`A_{M_{\mathrm{delivered}},\mathbf 1} = \dot V_F F_D`$ and
$`A_{M_{\mathrm{exhausted}},F_I} = \dot V_F`$.

**$`\dot V_F`$ appears in four of those five entries, and it does two
different jobs there**:

- **Delivery** is $`\dot V_F F_D`$, the litres of agent vapour arriving per
  second. It is a constant over the step, so it enters through the column of
  the unit state $`\mathbf 1`$.
- **Removal** is $`\dot V_F`$, the litres of mixed circuit gas leaving per
  second at the current fraction $`F_I`$. It is a coefficient on $`F_I`$, so it
  enters the diagonal and the $`M_{\mathrm{exhausted}}`$ row.

Today one symbol carries delivery and removal, because they are one stream on
the reference machine, a semi-closed circle with a bypass vaporizer. Every other
machine that the survey found separates them:

| Survey entry | Delivery | Removal |
| --- | --- | --- |
| (b3) direct injection into the circle | independent of $`\dot V_F`$ | unchanged |
| (b11) surplus gas valve closed | unchanged | zero |
| (b10) sidestream sample, not returned | unchanged | $`\dot V_F + \dot V_S`$ |
| (b1) dial is not the delivered concentration | $`F_D`$ is a function, not the dial | unchanged |

Written with the two rates, four of the five entries become

$$
A_{F_I,F_I} = -\frac{\dot m_{\mathrm{out}} + \dot V_A}{V_C},\qquad
A_{F_I,\mathbf 1} = \frac{\dot m_{\mathrm{in}}}{V_C},\qquad
A_{M_{\mathrm{delivered}},\mathbf 1} = \dot m_{\mathrm{in}},\qquad
A_{M_{\mathrm{exhausted}},F_I} = \dot m_{\mathrm{out}}
$$

The ventilation entry $`A_{F_I,F_A}`$ is unchanged, because it belongs to the
patient.

**On the reference machine, $`\dot m_{\mathrm{in}} = \dot V_F F_D`$ and
$`\dot m_{\mathrm{out}} = \dot V_F`$, so the matrix is entry-for-entry what it is
today.** The change that introduces the two rates is safe to merge, because it
changes no computed value. The existing reference tests in `tests/reference/` prove it, with their expected values unchanged.

### Two admissibility conditions, both structural

The three conditions below decide which machines fit this abstraction. The
exact propagator, $`\exp(A\,\Delta t)`$, needs the first two. If a machine fails
either one, it does more than reduce accuracy: it breaks a guarantee that the
solver rests on.

1. **Linear and time-invariant across a step.** $`\exp(A\,\Delta t)`$ is exact
   only because every setting is held constant within the step. When a
   machine's rates change with the state *during* the step, the matrix $`A`$
   becomes a function of the state $`y`$ and the propagator stops being exact.
   One such machine has a closed-loop controller that reads $`F_A`$ and moves
   the dial.
2. **Nonnegative off-diagonal entries in $`A`$ (a Metzler matrix).** They keep
   every compartment from going negative. The matrix-exponential routine
   (`core/matrix_exponential.py`) requires them. Both $`A_{F_I,\mathbf 1}`$ and
   $`A_{M_{\mathrm{exhausted}},F_I}`$ are off-diagonal, so **both rates must be
   nonnegative and finite**. A machine must not remove agent by delivering a
   negative rate.
3. **Stateless.** A failed step is rolled back to the run state that the
   breathing circuit captured (`BreathingCircuit.capture_state()`). If a
   machine kept state of its own, such as a controller's integrator or a
   vaporizer's thermal mass, that state would have to be captured too.
   Otherwise a rollback would silently restore a different machine from the
   one the step began with. A machine with state of its own therefore needs a
   design change first, to extend what is captured and restored.

Automated end-tidal control fails the first and third conditions, so it is
planned separately (planned-milestone item 5) rather than as a machine in this
abstraction.

## Question 3: how a machine composes with the existing core

**The machine is a boundary condition.** It supplies the two rates above and
the apparatus volume. It appears nowhere in the state vector and holds no
agent. It has no way to write a patient row, so adding a machine cannot change
one. That is true by construction rather than by review, and it is the
guarantee that the design brief asks for (`PL-FG9D`).

In this design, which the matrix suggests, the machine supplies the fresh gas
exchange: delivery and removal integrated over one step. The circuit code
already has a record for the exchange (`FreshGasExchange`, which
`advance_fresh_gas()` in `core/circuit.py` returns). Today the circuit computes
that record from its own fields, and so hard-codes one machine.

A machine could instead contain or configure the circuit, and both fail:

- **A machine that *contains* the circuit** makes the circuit one of its
  components. Every new machine would then reach into the compartments of the
  validated uptake model (`AgentUptakeSystem`). The design brief asks that this
  be avoided (`PL-FG9D`).
- **A machine that *configures* the circuit** sets the circuit's volume and
  fresh gas flow (`circuit_volume_l`, `fresh_gas_flow_l_min`) at construction
  and then plays no further part. Today's code does this implicitly: the uptake
  model reads `data/machines/reference_circle_system.json` when it is built for
  an agent (`AgentUptakeSystem.for_agent()`). This arrangement cannot express
  direct injection (b3) or a closed surplus gas valve (b11), because those
  change the *form* of the exchange rather than its coefficients.

## Question 1: where the parameter/strategy line falls

**A difference between machines is data (a parameter) when it changes the
*value* of the delivery rate, the removal rate or the apparatus volume. It is
behavior (a strategy) when it changes the *formula* producing them.**

The line is decidable rather than a matter of judgment. A machine affects the
simulation only through those three quantities (§ "A machine changes only two
rates and one volume"), so each difference either enters one of the two rate
expressions as a coefficient or selects which expression is used.

Data files may not hold executable equations (`CLAUDE.md`), so a strategy
cannot go in one. The design gives it a place of its own.

### The closed set of behaviors

A machine's behavior has three independent slots: delivery, removal and dial
mapping. A named strategy from a registry in `core/` fills each slot. A machine
profile names one strategy for each slot, and cannot supply its own.

**A strategy is a pure function** of the profile fields it declares, the run's
current controls, and $`F_I`$. Question 6's answer rests on that declaration:
every difference between machines traces to a named field.

**Two rules apply to every strategy.** A strategy may not read a field it did
not declare. It may not be added to the registry without an entry in the tables
below, because the registry *is* the closed set. A registry member that this
document does not list is the "too permissive" failure that the design brief
names (`PL-FG9D`).

#### Delivery

The delivery strategy sets $`\dot m_{\mathrm{in}}`$:

| Name | Rate | From | Status |
| --- | --- | --- | --- |
| `fresh_gas_bypass` | $`\dot V_F F_D`$ | today's model | implemented, as the only path |
| `in_circle_injection` | injector rate, independent of $`\dot V_F`$ | (b3) | planned-milestone item 4 |

The Zeus IE's *fresh gas mode* is `fresh_gas_bypass` on the manufacturer's own
description — Meyer et al.: *"In this dosing mode the agent dosage performance
is equivalent to a conventional vaporizer."* So a machine with two delivery
modes is two profiles, or one profile with a mode selection, and half of it is
already built.

#### Removal

The removal strategy sets $`\dot m_{\mathrm{out}}`$:

| Name | Rate | From | Status |
| --- | --- | --- | --- |
| `fresh_gas_displacement` | $`\dot V_F + \dot V_S`$ | today's model, plus (b10) | implemented, with $`\dot V_S = 0`$ |
| `closed_circuit` | $`\dot V_S`$ | (b11), surplus valve shut | not implemented |

The sample draw $`\dot V_S`$ is *data* rather than a third strategy, because
one expression covers all three of the survey's sampling configurations: a
mainstream sensor and a returned sidestream sample both give
$`\dot V_S = 0`$, and a scavenged sidestream sample gives the sample flow. Two
formulas would be one formula and a branch nobody can see.

#### Dial mapping

The dial-mapping strategy produces $`F_D`$ from the dial position:

| Name | Mapping | From | Status |
| --- | --- | --- | --- |
| `variable_bypass` | dial is a partial-pressure fraction | today's model | implemented, as identity |
| `fixed_volume_percent` | dial is volumes percent | (b1), the Tec 6 | see below |

**The dial-mapping slot is where the design is put to the test, and that test
has not happened yet.** An item asks that the Tec 6 desflurane vaporizer be the
concrete second device class that the abstraction is designed against
(`PL-439V`). Meyer et al. state the difference in one sentence: *"The desflurane
vaporizer principle described here delivers a fixed volume percentage, making it
different from conventional vaporizers, which deliver fixed partial pressures."*
The two mappings differ by a factor of
$`P_{\mathrm{ambient}}/P_{\mathrm{reference}}`$. **This model has no ambient
pressure, so in its present domain the two agree everywhere.** The item for
recording the model's sea-level assumption (`PL-5K5C`) is what separates them.
Until that item is done, a profile that names `fixed_volume_percent` gets the
same numbers as one that names `variable_bypass`, and the test meant to tell the
two apart (`PL-439V`) passes on paper only.

The flow-dependence of the same devices is **not** in the mapping, and must not
be quietly added to it. Hendrickx et al. measured it: within 10% of dial for
isoflurane at 0.3–10 L/min, within 13% for desflurane at 0.5–1 L/min, and worse
outside those ranges. It is a declared limitation of both strategies until a
milestone models it, because a flow-dependent correction fitted here would move
every validated wash-in ratio without any measurement of *this* model saying it
should.

## Question 2: what keeps the machine profile small

**The admission rule is that a field exists only if something consumes it.** The
schema says what consumes each field and what the field changes. A field whose
consumer and effect nobody can state is not added: it is neither recorded as
interesting nor carried "because the manual has it".

**A field names its consumer, which is either the model or the comparison
table.** The comparison table is the machine's own panel, which Question 5
describes (`PL-WZVZ`). A field is admitted for the model as a coefficient in a
declared expression. A field for the table changes no number, but disambiguates
one that does, such as which of the survey's three sampling configurations a
$`\dot V_S`$ of zero *is*. That is the only ground on which a field for the table
is admitted. Naming the consumer stops this second ground becoming an escape
hatch for the first.

**If the admission rule is wrong, the cost is one field added late.** The rule
leaves out every specification in the survey's "Ruled out" section. That section
has seven categories, and the survey put each there by its own test: none has a
path to a computed value under the model as it will be through this milestone.
The rule is a mistake only if one of the seven turns out to change a number the
model computes. Each category already states the condition that would bring it
back, and those conditions are the monitoring for that mistake. The opposite
error costs a profile of specifications that nothing reads, which is the failure
that the design brief names (`PL-FG9D`).

**In testable form, adding a machine adds a row, not a column.** Once the
abstraction is right, a new machine is values for fields that already exist. A
machine that needs a *new field* is a design event: either the survey missed an
axis, or the field is trivia. The survey gains an entry first, then this
document's closed set or schema gains the member, and only *then* is the machine
added, never the other way round.

**A script will check that every profile has the same fields, each with a
consumer declared in the schema.** The testable form above is decidable, so the
check belongs in a script. The script reads every file in `data/machines/`, and
fails the moment a machine is added as a column. As the project's instructions
ask of the decidable part of a rule (`CLAUDE.md`), the script runs from a bare
checkout with no virtualenv, returns the same result on every run, and states
its rule where a reviewer can read it. Building the script under `tools/` is
work for the milestone that implements this design.

**Unknown is not a value.** A machine whose apparatus volume is unknown cannot
be added yet, and it is never given a plausible apparatus volume instead. This
rule comes from the survey, and Question 4's second refusal enforces it when a
profile is loaded.

### The schema

Per field, matching what `data/machines/reference_circle_system.json` already
does and adding the two bindings the rules above need:

```text
value, unit                what the model reads
consumer                   "model" or "attribution"
effect                     one clause: which rate or bound this changes
source, tier, adopted      docs/MODEL.md's source hierarchy, unchanged
```

The fields the survey's evidence admits:

| Field | Consumer | What it changes | Survey |
| --- | --- | --- | --- |
| `apparatus_volume_l` | model | $`V_C`$, hence $`\tau_C`$ | (a1) |
| `deliverable_fresh_gas_flow_range` | model | the flow bound, with the model envelope | (b8) |
| `minimum_total_flow_l_min`, `minimum_oxygen_flow_l_min` | model | refusals below the floor | (b8) |
| `agents` | model | which agents may be mounted at all | (b9) |
| `agent_limits` | model | per-agent dial maximum | (b2) |
| `sample_gas_flow_l_min` | model | $`\dot m_{\mathrm{out}}`$ | (b10) |
| `sample_gas_configuration` | attribution | which sampling a zero means | (b10) |
| `delivery`, `removal`, `dial_mapping` | model | which strategy runs | (b1), (b3), (b11) |
| `not_modelled` | attribution | what this profile does not claim | Question 4 |

The per-agent dial maximum (`agent_limits`) is one field, a mapping keyed by
agent, rather than a column per agent. Adding an agent adds a key inside every
profile, and that is agent-milestone work, not machine work.

**The maximum delivered concentration (`max_delivered_concentration_percent`)
is in the wrong place today**, and the survey proves it: desflurane's 18% is the
calibrated maximum of the Tec 6, which Johnston et al. characterised *"from 1%
to 18%"*, and `docs/MODEL.md` already names that provenance. Nothing about
desflurane itself sets its maximum at 18%. It belongs on the (machine, agent)
pair, as `agent_limits`. Moving it is a data migration, and is work for the
milestone that implements this design. Until then, the intersection rule in
§ "Which values belong to the machine, the run and the model" holds the two
together, and nothing displayed changes.

## Which values belong to the machine, the run and the model

The abstraction separates three things one file currently holds together.

**The machine owns what a machine specifies.** Apparatus volume, flow range and
floor, agents it can mount, per-agent dial maxima, sampling, and the three
strategy names.

**The run owns its opening conditions**: the opening fresh gas flow, the opening
dial position, and the patient circuit volume. None of these is a machine
specification, and the reason differs for each:

- **Opening fresh gas flow.** An earlier item reasoned that a fresh gas flow is
  a machine setting rather than a patient or agent property (`PL-8DJ7`). That
  rightly rules out the patient and the agent, but does not settle where the
  field lives. The survey supplies the fact that does: **no reachable source
  states a startup fresh gas flow for any surveyed machine.** A per-machine
  field would therefore be `unknown` on every real profile. Question 4's second
  refusal rejects a machine with an unknown required field, so a machine field
  would either block every machine or force each one to fabricate a number. The
  opening flow is instead an opening condition of a run: a teaching choice, as
  the shipped file's own `provenance_gap` already calls it. Where the field
  lives and what value it takes are independent questions, and a separate item
  decides the value (`PL-NM7X`).
- **Opening dial position** is the same kind of condition, and the code already
  treats it so: building the uptake model for an agent
  (`AgentUptakeSystem.for_agent()`) starts the vaporizer at that agent's 1 MAC.
  That is a convention about where a run opens, not a property of the agent or
  of any device.
- **Patient circuit volume.** The reason comes from the survey's section on
  apparatus volume (a1). $`V_C`$ is apparatus *plus* patient circuit, and the
  patient circuit is a consumable chosen per case. A machine profile cannot own
  $`V_C`$ outright.

**The apparatus volume (`apparatus_volume_l`) and the shipped circuit volume
(`circuit_volume_l`) are two quantities, not two names for one** (project
owner, 2026-09-27, ratified, over recording `circuit_volume_l` as the apparatus
alone, `PL-HGB6`). The apparatus volume is the machine's half of the split this
section describes. It includes the absorber and excludes the disposable patient
circuit, which is how the survey's section (a1) records every figure it found.
The circuit volume is $`V_C`$ whole, apparatus plus patient circuit, because the
model has one well-mixed gas compartment in front of the patient and the limbs
and Y-piece have nowhere else to be. A profile written today from Shin et al.'s
figures for a Perseus A500 therefore stores the 3.3 L that includes the patient
circuit, never the 2.1 L apparatus figure. The 2.1 L would give a
$`\tau_C = V_C/\dot V_F`$ of 31.5 s at 4 L/min, where 49.5 s is right. **The two
names stay distinct until the split is made:** the milestone that implements
this design moves the patient circuit to the run. From then, a machine profile
carries `apparatus_volume_l`, and the run supplies the rest of $`V_C`$. Today's
meaning of `circuit_volume_l` is written where a profile author reads it: in the
schema docstring, the data file and `docs/MODEL.md` (`PL-TBMX`).

**The model keeps its envelope.** The bounds in `core/supported_ranges.py` are
the domain the compartment model is claimed over, and they stay exactly where
they are. The effective limit on a control is the **intersection** of the model
envelope and the machine's deliverable range, each with its own name, source
and refusal message. The intersection is what stops a machine profile silently
widening the model's claimed validity. This design adopts that framing unchanged
from an earlier item (`PL-8PS6`).

### What is built so far

**Built, for the fresh gas flow alone, on 2026-09-20** (`PL-8PS6`). The row
above is in the tree: `deliverable_fresh_gas_flow_range` is a field on
`BreathingCircuitParameters` carrying a `DeliverableFreshGasFlowRange`, and
`BreathingCircuit` holds both claims and refuses in each one's own words.
`reference_circle_system.json` declares `null`, section (b8) having found no
reachable range for any surveyed machine, so the envelope alone binds and
nothing displayed changed. Two consequences for item 1's own work, recorded
here because this document is where its scope is read: the field is
**optional, defaulting to `None`**, which reads as *declares no range* rather
than as *unlimited*, so Question 4's refusal of an `unknown` in a field the
model reads applies to the required fields a real machine profile must supply
and not to this one; and `minimum_total_flow_l_min` was **not** built beside
it, because a machine's minimum total fresh gas flow is the same number as
that range's floor and the admission rule above forbids storing it twice.
`minimum_oxygen_flow_l_min` was not built either, on the same rule: it reaches
nothing the model computes until there is a hypoxic guard to consume it.

**Built, for the opening fresh gas flow, on 2026-09-27** (`PL-QW19`), which
brings the tree into line with § "The run owns its opening conditions" above.
`default_fresh_gas_flow_l_min` stays on the machine profile and is **optional,
defaulting to `None`**, read as *this profile states no startup flow* and never
as *this machine has none*, so Question 4's refusal of an `unknown` no longer
reaches it: a real profile states a startup flow only where a source publishes
one, and no surveyed machine has. A run built from a profile that states none
opens at `TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN` in `core/circuit.py`, the
4.0 L/min `reference_circle_system.json` stores, whose authority is that file's
teaching-default rationale and not any source. The file keeps its value and its
provenance row, so nothing displayed changed, and a profile whose declared
deliverable range excludes the fallback is refused when the run is built, as a
stated flow outside the range would be. The object that would own all three
opening conditions was not built, and this did not need it: the dial already
opens at the agent's 1 MAC by convention, the patient-circuit volume stays
inside `circuit_volume_l` until item 1's split, and the object, once built,
subsumes the fallback without undoing it.

### The reference breathing system

**The reference profile is a breathing system, not a machine, and stays one.**
In its file, `reference_circle_system.json`, the circuit volume
(`circuit_volume_l`) of 6.0 L is the assembled total of apparatus and patient
circuit, for three reasons:

1. The model has one well-mixed gas compartment in front of the patient, so the
   limbs and Y-piece can only be inside $`V_C`$, as the survey's section (a1)
   says.
2. The profile's provenance note on Targ et al. rejects their measured 9.86 L
   chiefly because their system held a reservoir bag standing in for the lung.
   That system's corrugated limbs and Y-piece were part of what was measured,
   so the note's "the apparatus alone" meant without the lung, not without the
   hoses, and the note now says so (`PL-TBMX`). The note adds the reference
   adult's 2.5 L alveolar compartment, the lung, to the stored figure before
   setting the sum against 9.86 L. The comparison therefore bears on counting
   a lung twice, and says nothing about how the 6.0 L divides between
   apparatus and patient circuit.
3. `docs/MODEL.md` compares the 6.0 L with Shin et al.'s totals that include the
   patient circuit, the Primus's 5.9 L, rather than with their apparatus figures.

**No source divides the 6.0 L between apparatus and patient circuit**, so
splitting it would invent two numbers where one is recorded. The profile
therefore keeps the stored figure. Its list of provenance gaps
(`provenance_gap`) declares that the figure is the sum (`PL-TBMX`). Real
machines are added beside the reference profile, not made by retrofitting it
into a machine it never claimed to be. Once the machine and the patient
circuit get separate volumes, a profile built from Shin et al.'s figures will
store a true apparatus volume and take its 1.2 L patient circuit from the
run. Until then, such a profile stores the total with the patient circuit, as
the paragraph on the two volumes above says.

## Question 4: validation and provenance per machine

**A machine module with no provenance fails to load rather than runs.** The
requirement comes from the item behind this design (`PL-FG9D`), and follows
from `CLAUDE.md`'s preference for an obvious failure state over a
plausible-looking number. The loader (`core/parameters.py`) refuses a profile
that:

1. **carries a field with no `source` and no entry in a `provenance_gap`** —
   the discipline `reference_circle_system.json` already meets, and the reason
   that file exists;
2. **carries `unknown` in a field the model reads** — the survey's rule, and
   the honest statement that most surveyed machines cannot be added yet;
3. **names a strategy not in the registry** — the closed set, enforced;
4. **declares an empty `not_modelled` list**; or
5. **declares a `schema_version` the loader does not know.**

Nothing in this adds vocabulary. `tier` and `adopted` are `docs/MODEL.md`
§ "Source hierarchy"'s, checked by `make check` against the existing closed
vocabulary, and a machine constant is held to the same three tiers as a
partition coefficient: a measurement outranks a specification sheet, and a
specification sheet is not a measurement. The survey already applies that
ruling to itself — Shin et al.'s apparatus volumes are recorded tier 2 because
that paper carries them rather than measured them.

Refusal 4 is the one worth arguing for. **Every machine has a non-empty
`not_modelled` list, and the survey is what proves it**: fresh gas inlet
position, ventilator drive, decoupling and the control loop all reach a number
and none is represented here. A profile claiming otherwise is claiming a
fidelity the model does not have, so an empty list is a defect rather than a
tidy result — and requiring it non-empty makes the omission a positive
statement the author had to write, which is what Question 5 then displays.

## Fresh gas inlet position is not modelled

**Decline to represent internal topology, and say so where a machine is
chosen.** Two machines differing only in inlet position are, in this model, the
same machine — and the interface states that rather than offering two names
that produce one curve.

**This is an instance, not a rule, and its condition is named.** It stops being
true when item 39 lands a per-compartment gas-phase model, or when any
multi-limb circuit enters the model. Written as a rule it would outlive its
own evidence and be obeyed by sessions that were not here.

The survey's headline finding is that **apparatus volume alone does not explain
the measured differences between machines**, and its sharpest instance is
Fukuda et al.'s randomised patient study: moving only the fresh gas inlet
significantly raised the inspired/delivered ratio of isoflurane and of
sevoflurane during low-flow anesthesia. $`F_I/F_D`$ is the ratio this model's
circuit equation *is*, and a machine changed it with volume held fixed.

A single well-mixed compartment has no place to put that. The survey named
three options and refused one. Besides the decline above, they are:

- **Refused: fold it into an effective volume.** The survey's refusal stands
  and is worth restating, because it is the option an implementation reaches
  for. Calibrating a volume to reproduce observed kinetics would fit the curves
  and attribute to volume a difference volume did not cause. `PL-WZVZ`'s table
  would then print a sourced-looking number no measurement supports, which is
  the exact failure that table exists to prevent.
- **Not now: represent inlet position.** A multi-limb circuit separates inspired
  gas from mean circuit gas. Under a model such as Lerou and Booij's, the two
  become distinct states, and this model's single $`F_I`$ stops describing both.
  `docs/MODEL.md` § "Model boundary" already names that consequence, and the
  departure has to be recorded there before the model is extended that way.
  Representing inlet position changes the model boundary, so it belongs to
  planned-milestone item 39 (per-compartment gas-phase condition), not to
  item 1.

**Declining is not merely the cheap option: it is needed under *either*
answer.** Even once planned-milestone item 39 is built, a machine whose inlet
position is unknown still needs the interface's statement that inlet position
is not modelled. Every surveyed machine is such a machine, except the two that
Fukuda et al. instrumented. Building item 39 first would change which machines
the statement covers, not whether the statement is required.

## Question 5: naming a real machine in the interface

**Decided (project owner, 2026-09-20, ratified)**, on this session's
recommendation and over naming the machine by its trade name in the running
interface. It is what a learner sees, so the decision was theirs; the case
below is the one they ratified rather than one they authored, which is the
distinction `CLAUDE.md` asks to be recorded — **ordinary evidence reopens it**:
a measurement, a cost this case did not carry, or a constraint that appears
later.

**Show the archetype in the running interface, and attach the trade name to the
parameter set.** The machine chooser and the dashboard name a machine by what
the model represents, such as
"circle system · 3.3 L with patient circuit · variable-bypass vaporizer". The
trade name appears in the machine's own panel, beside its parameters, its
sources and its `not_modelled` list. There it is a citation rather than a
claim.

**The decision binds the comparison table, planned-milestone item 1 and the
`not_modelled` list.** The item behind the comparison table between machines
(`PL-WZVZ`) builds that panel, so the table and the machine's own parameter set
are the same surface. A trade name may appear there and may not appear on a
curve, a chooser entry or a dashboard readout. For planned-milestone item 1,
that is a scope constraint, not a preference. The `not_modelled` list becomes
more than a provenance record: a trade name may appear only where that list is
on screen beside it.

Three facts decide where the trade name goes, and none is a matter of taste:

1. **The model reproduces a known-incomplete subset, and the survey measured
   the shortfall.** Shin et al. found the Perseus A500 and Zeus IE
   indistinguishable on volume: 2.1 L against 2.0 L of apparatus, 3.3 L
   against 3.2 L with the 1.2 L patient circuit, and time constants of 6.6
   against 6.4 min at 0.5 L/min. The two still differed significantly in time
   to target, and Shin et al. attributed the remaining difference to inlet
   position, decoupling, ventilator drive and delivery mode. Every one of those
   is in this model's `not_modelled` list.
2. **The decline in § "Fresh gas inlet position is not modelled" makes some
   machines identical here.** Under a trade-name label the interface would
   offer two names that produce one curve, with nothing saying why. Under an
   archetype label it offers one entry, correctly.
3. **`CLAUDE.md`'s clinical-output standard already governs the choice.** The
   correct number with the wrong model identity is a presentation failure, and
   a learner who reads a trade name on a curve attributes the curve to the
   machine on the wall in their operating room.

The two other options are weaker:

- **Full trade name everywhere** makes the feature feel real, and users will
  ask for it. It claims the most and has the least support, and the survey's
  measurement argues directly against it.
- **Archetype only, no trade name anywhere** is safe but throws away the
  provenance: a reader cannot check a parameter against a manual for a machine
  nobody names.

The decision is the middle one because it keeps the trade name exactly where
the evidence for it is on screen.

## Question 6: every difference between machines traces to a named field

**Every difference a machine makes to a curve can be traced to declared
fields.** The item behind this design (`PL-FG9D`) asks for this as a constraint
on the design, not only on the display: *design so that the parameter set is the
explanation*. A machine affects the model only through the three quantities that
§ "A machine changes only two rates and one volume" names, and each comes from
declared fields:

- the volume $`V_C`$: the apparatus volume (`apparatus_volume_l`) plus the run's
  patient-circuit volume, which today is the assembled circuit volume
  (`circuit_volume_l`);
- the inflow $`\dot m_{\mathrm{in}}`$: the `delivery` strategy and the fields it
  declares;
- the outflow $`\dot m_{\mathrm{out}}`$: the `removal` strategy and the sample
  gas flow (`sample_gas_flow_l_min`).

**There is nowhere else for a difference to hide**, because the design forbids
two things: a strategy that reads an undeclared field, and one outside the
registry. Question 1 explains both.

**The comparison table between machines (`PL-WZVZ`) is therefore derived.** For
any two machine profiles, the fields that differ can be computed, and the
`effect` clause that the schema already requires says what each one does. A
derived table stays true, while one maintained by hand can go out of date.

**The design rules out a difference that nobody could explain to a learner.**
Such a difference would arise if a machine changed a result through something
unnamed, for example a default inside a strategy or a branch on an undeclared
field. The interface would then attribute it to the machine's trade name. That
is an unsafe display, and the item behind the comparison table (`PL-WZVZ`)
exists to prevent it. With this design, that item does not have to catch it.

## Question 7: what the second machine costs

A second machine falls into one of three cases, and only the first is a
data-entry task. The costs below are the target that the item behind this
design (`PL-FG9D`) asks for.

**A machine whose delivery and removal strategies are already in the closed
set: one data file, and nothing else.** The machine needs one JSON file under
`src/anesthesia_sim/data/machines/`, naming one strategy from each of the three
slots, with every field sourced and a non-empty `not_modelled` list. **It needs
no change to `core/`, no change to any patient row and no new test of the
physics.** The physics is the matrix, which is already tested, and the new
machine can reach it only through the two rates. Beyond the file, the machine
needs a schema test and its row in the comparison table between machines
(`PL-WZVZ`). The cost can be checked: the diff touches one file under
`data/machines/` and one test file.

**A machine needing a new strategy: a design event, and a bounded one.** It
needs one registry entry, one pure function that returns a rate, a proof that
the rate meets the two admissibility conditions, and a row in this document's
closed set. The two conditions are that the rate is nonnegative and finite, and
that it is constant across a step. Such a machine still needs no change to any
patient row or to the solver.

**A machine needing a new profile field: a design event that starts in the
survey.** The field is added to `docs/machine-survey.md` with the stated path
from it to a computed value, then to the schema with its consumer and effect,
then to every existing profile, and only then is the machine added, never the
other way round. Adding the field to every existing profile is the cost that
keeps the schema honest: a field added for one machine must be answerable for
all of them, or it is trivia.

**If the design cannot state what a second machine costs, it is not
finished.** That is the test set by the item behind this design (`PL-FG9D`).
The design states the cost, and the column check under Question 2 can verify
the statement.

## What this design does not decide

None of the following is settled. Each entry records what is already known, so
that nobody works it out again from scratch.

- **The value of the opening fresh gas flow.** It is the project owner's
  decision (`PL-NM7X`). Where the opening flow belongs is decided in
  § "Which values belong to the machine, the run and the model".
- **Whether the model gains an ambient pressure.** An item tracks it
  (`PL-5K5C`). Until the model gains one, Question 1's § "Dial mapping" says
  what follows.
- **Flow-dependent vaporizer output.** No milestone models it. Question 1's
  § "Dial mapping" records it as a limitation of both mapping strategies.
- **Ventilation, decoupling and the ventilator.** (b5) and (b6) have a path to
  a computed value only once the machine owns the ventilator, and this
  abstraction does not give it the ventilator. Ventilation stays a patient-side
  control. Decoupling is a fourth strategy slot, opened by whichever milestone
  moves it.
- **Automated end-tidal control.** It is left to planned-milestone item 5, for
  the reason that ends § "A machine changes only two rates and one volume".
- **Every `unknown` in the survey.** The survey records apparatus volumes, flow
  floors, agent lists and sample flows as unknown for the GE and Getinge
  machines, and for three of the five Dräger ones. Its last section names the
  manuals and the route. **These unknowns are a condition on each profile, not
  on this abstraction.** The loader refuses a profile with `unknown` in a field
  the model reads, so such a machine stays out until its fields are known. That
  machine's manual is sought when its profile is built, not in advance (project
  owner, 2026-09-20). The design is complete without any of these values:
  meanwhile it runs on the reference profile by construction, not for want of
  evidence.

## Sources

Every source below is cited in `docs/machine-survey.md`, which records the
retrieval route, the depth of reading and the full bibliographic record for
each, and remains the authority for all of them. This list names only the
sources this document reasons from.

- Fukuda T, Fukunaga A, Toyooka H. *J Anesth.* 2006;20(4):268–273 — inlet
  position changes $`F_I/F_D`$ at fixed volume, the measurement behind
  § "Fresh gas inlet position is not modelled".
- Hendrickx JF, De Cooman S, Deloof T, et al. *Anesth Analg.*
  2001;93(2):391–395 — cassette-vaporizer output against dial across flow;
  used in Question 1's § "Dial mapping".
- Johnston RV, Andrews JJ, Deyo DJ, et al. *Anesth Analg.* 1994;79(3):548–552 —
  the Tec 6 characterised from 1% to 18%, the provenance of the 18; used in
  Question 2's § "The schema".
- Meyer J-U, Kullik G, Wruck N, Kück K, Manigel J. In: Schüttler J, Schwilden
  H, eds. *Modern Anesthetics.* Springer; 2008:451–470 — the Zeus's two dosing
  modes, the closed surplus gas valve, the gas module's sample draw, and the
  fixed-volume-percentage principle; used in Question 1.
- Shin HW, Yu HN, Bae GE, et al. *BMC Anesthesiol.* 2017;17(1):10 — the three
  Dräger apparatus volumes, and machines indistinguishable on volume that still
  differ significantly in time to target; used in § "Which values belong to the
  machine, the run and the model", Question 4 and Question 5.
- Targ AG, Yasuda N, Eger EI II. *Anesth Analg.* 1989;69(2):218–225 — the
  measured 9.86 L that the reference profile's provenance note reasons against;
  used in § "The reference breathing system".
