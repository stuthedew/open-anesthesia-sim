# The anesthesia-machine abstraction: what a machine module is

## What this document is, and what it is not

`ROADMAP.md`'s planned-milestone item 1 commits to a modular anesthesia-machine
abstraction whose point is that **a real commercial machine can be added as a
module**. `docs/machine-survey.md` established which ways real machines differ
actually reach a number this simulator computes. This document is the design
that survey exists to serve: what a module *is*, what the base owns against
what each machine supplies, where the parameter/strategy line falls, and what
the second machine costs.

**Design only.** Nothing here changes `src/`. No machine class, no interlocks,
no data migration: those are planned-milestone item 1's, and this document is
what makes that milestone scopeable. Where a decision below implies work, the
work is named and left to the milestone.

**Not held to the tree.** `docs/MODEL.md` specifies the model *as implemented*
and its § "How this document is held to the tree" binds every live assertion in
it to something a script can resolve. This design is not implemented, so
writing it into that document would put unresolvable assertions inside a bound
one. It sits beside `docs/machine-survey.md` for the same reason, and
`docs/MODEL.md` gains its statements when item 1 lands them.

## The finding the whole design rests on

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
agent. It has no way to write a patient row, so adding a machine cannot change one. That is true by construction rather than by review, and it is the guarantee the item asks for.

In this design, which the matrix suggests, the machine supplies the fresh gas
exchange: delivery and removal integrated over one step. The circuit code
already has a record for the exchange (`FreshGasExchange`, which
`advance_fresh_gas()` in `core/circuit.py` returns). Today the circuit computes
that record from its own fields, and so hard-codes one machine.

A machine could instead contain or configure the circuit, and both fail:

- **A machine that *contains* the circuit** makes the circuit one of its
  components. Every new machine would then reach into the compartments of the
  validated uptake model (`AgentUptakeSystem`). The item asks the design to
  avoid this.
- **A machine that *configures* the circuit** sets the circuit's volume and
  fresh gas flow (`circuit_volume_l`, `fresh_gas_flow_l_min`) at construction
  and then plays no further part. Today's code does this implicitly: the uptake
  model reads `data/machines/reference_circle_system.json` when it is built for
  an agent (`AgentUptakeSystem.for_agent()`). This arrangement cannot express
  direct injection (b3) or a closed surplus gas valve (b11), because those
  change the *form* of the exchange rather than its coefficients.

## Question 1: where the parameter/strategy line falls

**A difference between machines is data (a parameter) when it changes the
*value* of one of the three quantities. It is behavior (a strategy) when it
changes the *formula* producing them.**

The line is decidable rather than a matter of judgment. A machine affects the simulation only through the three quantities, so each difference either enters one of the two rate expressions as a coefficient or selects which expression is used.

Data files may not hold executable equations (`CLAUDE.md`), so a strategy
cannot go in one. The design gives it a place of its own.

### The closed set of behaviors

Three independent slots, each filled by a named strategy from a registry in
`core/`. A machine profile names one from each; it cannot supply one.

**Delivery — what fills $`\dot m_{\mathrm{in}}`$:**

| Name | Rate | From | Status |
| --- | --- | --- | --- |
| `fresh_gas_bypass` | $`\dot V_F F_D`$ | today's model | implemented, as the only path |
| `in_circle_injection` | injector rate, independent of $`\dot V_F`$ | (b3) | planned-milestone item 4 |

The Zeus IE's *fresh gas mode* is `fresh_gas_bypass` on the manufacturer's own
description — Meyer et al.: *"In this dosing mode the agent dosage performance
is equivalent to a conventional vaporizer."* So a machine with two delivery
modes is two profiles, or one profile with a mode selection, and half of it is
already built.

**Removal — what fills $`\dot m_{\mathrm{out}}`$:**

| Name | Rate | From | Status |
| --- | --- | --- | --- |
| `fresh_gas_displacement` | $`\dot V_F + \dot V_S`$ | today's model, plus (b10) | implemented, with $`\dot V_S = 0`$ |
| `closed_circuit` | $`\dot V_S`$ | (b11), surplus valve shut | not implemented |

The sample draw $`\dot V_S`$ is *data* rather than a third strategy, because
one expression covers all three of the survey's sampling configurations: a
mainstream sensor and a returned sidestream sample both give
$`\dot V_S = 0`$, and a scavenged sidestream sample gives the sample flow. Two
formulas would be one formula and a branch nobody can see.

**Dial mapping — what produces $`F_D`$ from the dial position:**

| Name | Mapping | From | Status |
| --- | --- | --- | --- |
| `variable_bypass` | dial is a partial-pressure fraction | today's model | implemented, as identity |
| `fixed_volume_percent` | dial is volumes percent | (b1), the Tec 6 | see below |

**This slot is where the design is tested and where it is currently honest
about being untested.** `PL-439V` asks that the Tec 6 be the concrete second
device class the abstraction is designed against, and Meyer et al. state the
difference in one sentence: *"The desflurane vaporizer principle described here
delivers a fixed volume percentage, making it different from conventional
vaporizers, which deliver fixed partial pressures."* The two mappings differ by
a factor of $`P_{\mathrm{ambient}}/P_{\mathrm{reference}}`$ — **and this model
has no ambient pressure, so in its present domain the two functions agree
everywhere.** The slot is real, the second member is named, and it is currently
a declared coincidence rather than a distinction: `PL-5K5C` (record the model's
sea-level assumption) is what separates them, and until it lands a profile
naming `fixed_volume_percent` gets the same numbers as one naming
`variable_bypass`. Recording that is the point; discovering it during
implementation is what this document exists to prevent.

Hendrickx et al.'s measured flow-dependence of the same devices — within 10%
of dial for isoflurane at 0.3–10 L/min, within 13% for desflurane at
0.5–1 L/min, worse outside those ranges — is **not** in the mapping and must
not be quietly added to it. It is a declared limitation of both strategies
until a milestone models it, because a flow-dependent correction fitted here
would move every validated wash-in ratio without any measurement of *this*
model saying it should.

**A strategy is a pure function** of the profile fields it declares, the run's
current controls, and $`F_I`$ — and it declares which fields it reads. That
declaration is what Question 6 rests on.

**Two refusals, recorded so they are not re-proposed.** A strategy may not read
a field it did not declare; and a strategy may not be added to the registry
without an entry in the table above, because the registry *is* the closed set
and a member outside this document is the "too permissive" failure the item
names.

## Question 2: what keeps the machine profile small

**The admission rule.** A field exists only if something consumes it, and the
schema says what consumes it and what it changes. A field nobody can say that
about is not added — not recorded as interesting, not carried "because the
manual has it".

**Two consumers, and a field names which.** The model is one: the field is a
coefficient in a declared expression. `PL-WZVZ`'s comparison table is the
other: a field that reaches no number but disambiguates one that does — which
of the survey's three sampling configurations a $`\dot V_S`$ of zero *is* — is
admissible on that ground and on no other. Naming the consumer is what stops
the second ground becoming an escape hatch for the first.

**The testable form: adding a machine adds a row, not a column.** Once the
abstraction is right, a new machine is values for fields that already exist. A
machine needing a *new field* is a design event — the survey missed an axis, or
the field is trivia — and the route is: the survey gains an entry, this
document's closed set or schema gains the member, *then* the machine is added.
Never the other way.

**That is decidable, so it belongs in a script rather than in this paragraph.**
A check under `tools/` reading every file in `data/machines/`, asserting that
the key sets are identical across profiles and that every key appears in the
schema's declared-consumer list, fails the moment a machine is added as a
column. It runs from a bare checkout with no virtualenv, answers identically
every run, and states its rule where a reviewer can read it, which is what
`CLAUDE.md` asks of the decidable half of a rule. Building it is item 1's.

**Unknown is not a value.** The survey's rule carries straight through: an
unknown apparatus volume is a machine that cannot be added yet, not a machine
with a plausible apparatus volume. See Question 4 for what that does at load
time.

**What the rule is wrong about, if it is wrong.** It suppresses every machine
specification the survey put in its "Ruled out" section — seven categories,
each already carrying the condition that brings it back. The rule is a mistake
only if one of those turns out to reach a number the model computes, and the
survey's own test is what put them there: none has a path to a computed value
under the model as it will be through this milestone. The cost of being wrong
is one field added late; the cost of the opposite error is a profile of
specifications nothing reads, which is the failure mode the item names. Those
condition lines are the monitoring, and they are already written.

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

`agent_limits` is a mapping keyed by agent, which is one field rather than a
column per agent: adding an agent adds a key inside every profile, and that is
agent-milestone work, not machine work.

**`apparatus_volume_l` and the tree's `circuit_volume_l` are two quantities,
not two names for one** (project owner, 2026-09-27, ratified, over recording
`circuit_volume_l` as the apparatus alone, `PL-HGB6`). `apparatus_volume_l` is
the machine's half of the split under § "Three homes, and why the shipped
constants move" below: the apparatus including its absorber and excluding the
disposable patient circuit, which is how the survey's section (a1) records every
figure it found. `circuit_volume_l`, the field the tree ships, is $`V_C`$ whole:
it is the assembled total, apparatus plus patient circuit, because the model has
one well-mixed gas compartment in front of the patient and the limbs and Y-piece
have nowhere else to be. So a
profile written today from Shin et al.'s figures for a Perseus A500 stores the
with-circuit 3.3 L, never the 2.1 L apparatus figure, which would give a
$`\tau_C = V_C/\dot V_F`$ of 31.5 s at 4 L/min where 49.5 s is right. **The
condition is the split itself:** the two names stay distinct until item 1 moves
the patient circuit to the run, and from then a machine profile carries
`apparatus_volume_l` and the run supplies the rest of $`V_C`$. `PL-TBMX` wrote
today's meaning where a profile author reads it — the schema docstring, the
data file and `docs/MODEL.md`.

### Three homes, and why the shipped constants move

The abstraction separates three things one file currently holds together.

**The machine owns what a machine specifies.** Apparatus volume, flow range and
floor, agents it can mount, per-agent dial maxima, sampling, and the three
strategy names.

**The run owns its opening conditions.** The opening fresh gas flow, the
opening dial position, and the patient circuit volume. None of these is a
machine specification, and the reasoning differs per field:

- **Opening fresh gas flow.** `PL-8DJ7` deferred this field's home to this
  abstraction, on the reasoning that a fresh gas flow is a machine setting
  rather than a patient or agent property. That reasoning is right about which
  side of the patient/agent split it falls on and does not settle the home,
  and the survey supplies the fact that does: **no reachable source states a
  startup fresh gas flow for any surveyed machine.** A per-machine field would
  therefore be `unknown` on every real profile — and under the rule directly
  above, a machine with an unknown required field cannot be added. So making
  it a machine field would either block every machine or force each one to
  fabricate a number. It is an opening condition of a run: a teaching choice,
  which is exactly what the shipped file's own `provenance_gap` already calls
  it. `PL-NM7X` decides the *value* and is unaffected by this; the two
  questions are independent.
- **Opening dial position** is the same shape and is already in the tree:
  `AgentUptakeSystem.for_agent()` starts the vaporizer at that agent's 1 MAC,
  which is a convention about where a run opens rather than a property of the
  agent or of any device.
- **Patient circuit volume** is the survey's (a1) consequence. $`V_C`$ is
  apparatus *plus* patient circuit, and the patient circuit is a consumable
  chosen per case. A machine profile cannot own $`V_C`$ outright.

**The model keeps its envelope.** `core/supported_ranges.py`'s bounds are the
domain the compartment model is claimed over, and they stay exactly where they
are. The effective limit on a control is the **intersection** of the model
envelope and the machine's deliverable range, each with its own name, source
and refusal message. That is `PL-8PS6`'s framing and this design adopts it
unchanged; it is also what stops a machine profile silently widening the
model's claimed validity.

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

**The reference profile is a breathing system, not a machine, and stays one.**
`reference_circle_system.json` is named for what it is. Its `circuit_volume_l`
of 6.0 L is the assembled total, apparatus plus patient circuit, on three
grounds. The model has one well-mixed gas compartment in front of the patient,
so the limbs and Y-piece can only be inside $`V_C`$, as the survey's section
(a1) says. The file's Targ et al. note refuses the measured 9.86 L chiefly
because that system held a reservoir bag standing in for the lung, while its
corrugated limbs and Y-piece were part of the system measured, so the note's
"the apparatus alone" meant without the lung, not without the hoses, which is
what `PL-TBMX` reworded it to say. And
`docs/MODEL.md` sets it beside Shin et al.'s with-circuit totals, the Primus's
5.9 L, rather than beside their apparatus figures. What the note's comparison
adds to the stored figure before setting it against the measured 9.86 L is the
reference adult's 2.5 L alveolar compartment, the lung, so it bears on counting
a lung twice and says nothing about how the 6.0 L divides between apparatus and
patient circuit. **No source apportions it**, so splitting it into an apparatus
volume and a patient-circuit volume would invent two numbers where one is
recorded. It therefore keeps its stored figure with a declared statement that
it is the sum, which `PL-TBMX` wrote into its `provenance_gap`, and real
machines are added beside it
rather than by retrofitting it into a machine it never claimed to be. A profile
built from Shin et al.'s figures carries a true apparatus volume once the split
lands and takes its 1.2 L patient circuit from the run; until then it stores
the with-circuit total, as the paragraph under the schema table says.

**`max_delivered_concentration_percent` is mislocated today**, and the survey
proves it rather than arguing it: desflurane's 18% is the calibrated maximum of
the Tec 6, which Johnston et al. characterised *"from 1% to 18%"*, and
`docs/MODEL.md` already names that provenance. Nothing about desflurane binds
it to 18%. It belongs on the (machine, agent) pair as `agent_limits`. Moving it
is item 1's work and a data migration; until then the intersection rule above
holds the two together and nothing displayed changes.

## Question 4: validation and provenance per machine

**A machine module with no provenance fails to load rather than runs.** That is
the item's requirement and it follows from `CLAUDE.md`'s preference for an
obvious failure state over a plausible-looking number. Concretely, `core/parameters.py`
refuses a profile that:

1. **carries a field with no `source` and no entry in a `provenance_gap`** —
   the discipline `reference_circle_system.json` already meets, and the reason
   that file exists;
2. **carries `unknown` in a field the model reads** — the survey's rule, and
   the honest statement that most surveyed machines cannot be added yet;
3. **names a strategy not in the registry** — the closed set, enforced;
4. **declares an empty `not_modelled` list**; or
5. **declares a `schema_version` the loader does not know.**

Item 4 is the one worth arguing for. **Every machine has a non-empty
`not_modelled` list, and the survey is what proves it**: fresh gas inlet
position, ventilator drive, decoupling and the control loop all reach a number
and none is represented here. A profile claiming otherwise is claiming a
fidelity the model does not have, so an empty list is a defect rather than a
tidy result — and requiring it non-empty makes the omission a positive
statement the author had to write, which is what Question 5 then displays.

Nothing in this adds vocabulary. `tier` and `adopted` are `docs/MODEL.md`
§ "Source hierarchy"'s, checked by `make check` against the existing closed
vocabulary, and a machine constant is held to the same three tiers as a
partition coefficient: a measurement outranks a specification sheet, and a
specification sheet is not a measurement. The survey already applies that
ruling to itself — Shin et al.'s apparatus volumes are recorded tier 2 because
that paper carries them rather than measured them.

## Question 6: attributability

**Every difference a machine makes to a curve can be traced to declared
fields.** The item asks for this as a constraint on the design, not only on the
display: *design so that the parameter set is the explanation*. A machine
affects the model only through three quantities:

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

## The inlet-position decision, taken on the record

The survey's headline finding is that **apparatus volume alone does not explain
the measured differences between machines**, and its sharpest instance is
Fukuda et al.'s randomised patient study: moving only the fresh gas inlet
significantly raised the inspired/delivered ratio of isoflurane and of
sevoflurane during low-flow anesthesia. $`F_I/F_D`$ is the ratio this model's
circuit equation *is*, and a machine changed it with volume held fixed.

A single well-mixed compartment has no place to put that. The survey named
three options and refused one. Taking the remaining choice on the record:

**Decline to represent internal topology, and say so where a machine is
chosen.** Two machines differing only in inlet position are, in this model, the
same machine — and the interface states that rather than offering two names
that produce one curve.

- **Refused: fold it into an effective volume.** The survey's refusal stands
  and is worth restating, because it is the option an implementation reaches
  for. Calibrating a volume to reproduce observed kinetics would fit the curves
  and attribute to volume a difference volume did not cause. `PL-WZVZ`'s table
  would then print a sourced-looking number no measurement supports, which is
  the exact failure that table exists to prevent.
- **Not now: represent it.** A multi-limb circuit separates inspired gas from
  mean circuit gas, and `docs/MODEL.md` § "Model boundary" already names the
  consequence — under a model such as Lerou and Booij's the two become distinct
  states, this model's single $`F_I`$ stops describing both, and the departure
  has to be recorded there before the model is extended that way. That is a
  change to the model boundary, which is planned-milestone item 39's
  (per-compartment gas-phase condition), not item 1's.
- **Why declining is not merely the cheap option.** The decline is needed
  under *either* answer. Even with item 39 built, a machine whose inlet
  position is unknown — which is every surveyed machine but the two Fukuda
  et al. instrumented — still needs the statement. Building item 39 first would
  change which machines the statement covers, not whether it is owed.

**This is an instance, not a rule, and its condition is named.** It stops being
true when item 39 lands a per-compartment gas-phase model, or when any
multi-limb circuit enters the model. Written as a rule it would outlive its
own evidence and be obeyed by sessions that were not here.

## Question 5: naming a real machine in the interface

**Decided (project owner, 2026-09-20, ratified)**, on this session's
recommendation and over naming the machine by its trade name in the running
interface. It is what a learner sees, so the decision was theirs; the case
below is the one they ratified rather than one they authored, which is the
distinction `CLAUDE.md` asks to be recorded — **ordinary evidence reopens it**:
a measurement, a cost this case did not carry, or a constraint that appears
later.

**Show the archetype in the running interface; attach the trade name to the
parameter set.** The machine chooser and the dashboard name a machine by what
the model represents —
"circle system · 3.3 L with patient circuit · variable-bypass vaporizer" — and
the trade name appears in the machine's own panel, beside its parameters, its
sources and its `not_modelled` list. The trade name becomes a citation rather
than a claim.

Three facts decide it, and none is a matter of taste:

1. **The model reproduces a known-incomplete subset, and the survey measured
   the shortfall.** Shin et al. found the Perseus A500 and Zeus IE
   indistinguishable on volume — 2.1 L against 2.0 L of apparatus, 3.3 L
   against 3.2 L with the 1.2 L patient circuit, time constants of 6.6 against
   6.4 min at 0.5 L/min — and still significantly different in
   time to target, attributing the residue to inlet position, decoupling,
   ventilator drive and delivery mode. Every one of those is in this model's
   `not_modelled` list.
2. **The decline above makes some machines identical here.** Under a trade-name
   label the interface would offer two names that produce one curve, with
   nothing saying why. Under an archetype label it offers one entry, correctly.
3. **`CLAUDE.md`'s clinical-output standard already governs it.** The correct
   number with the wrong model identity is a presentation failure, and a
   learner who reads a trade name on a curve attributes the curve to the
   machine on the wall in their operating room.

The weaker options, so the choice is visible rather than asserted. **Full trade
name everywhere** is what makes the feature feel real and is what a user will
ask for; it claims the most and is supported the least, and it is the option
the survey's measurement argues directly against. **Archetype only, no trade
name anywhere** is safe and throws away the provenance: a reader cannot check a
parameter against a manual for a machine nobody names. The decision is the
middle one because it keeps the trade name exactly where the evidence for it is
on screen.

**What this binds.** `PL-WZVZ` builds the panel this puts the trade name in, so
its comparison table and the machine's own parameter set are the same surface:
a trade name may appear there and may not appear on a curve, a chooser entry or
a dashboard readout. Planned-milestone item 1 inherits that as a scope
constraint rather than a preference, and the `not_modelled` list stops being a
provenance record only — it is what has to be on screen beside the trade name
for the trade name to be admissible at all.

## Question 7: what the second machine costs

Stated as the target the item asks for. Three cases, and only the first is a
data-entry task.

**A machine whose delivery and removal are already in the closed set: one data
file, and nothing else.** One JSON file under `src/anesthesia_sim/data/machines/`,
naming one strategy from each of the three slots, with every field sourced and
a non-empty `not_modelled` list. **No change to `core/`, no change to any
patient row, no new test of the physics** — the physics is the matrix, it is
already tested, and the new machine cannot reach it except through the two
rates. What the machine owes is a schema test and its row in `PL-WZVZ`'s
comparison. Measurable: the diff touches one file under `data/machines/` and
one test file.

**A machine needing a new strategy: a design event, and a bounded one.** One
registry entry, one pure function returning a rate, a proof that it satisfies
the two admissibility conditions — nonnegative and finite, constant across a
step — and a row in this document's closed set. Still no patient row, still no
change to the solver.

**A machine needing a new profile field: a design event that starts in the
survey.** The field is added to `docs/machine-survey.md` with the stated path
from it to a computed value, then to the schema with its consumer and effect,
then to every existing profile. That last clause is the cost that keeps the
schema honest: a field added for one machine must be answerable for all of
them, or it is trivia.

**If the design cannot state that, it is not finished** — the item's own test.
It states it, and the statement is checkable by the column check under Question
2.

## What this design does not decide

Recorded so the milestone does not mistake them for settled, and so nothing
below is re-derived from scratch.

- **The value of the opening fresh gas flow.** `PL-NM7X`, the project owner's.
  This document decides only that it is an opening condition of a run rather
  than a machine specification.
- **Whether the model gains an ambient pressure.** `PL-5K5C`. Until it does,
  `variable_bypass` and `fixed_volume_percent` agree everywhere in the model's
  domain, and `PL-439V`'s discriminating test passes on paper only.
- **Flow-dependent vaporizer output.** Hendrickx et al. measured it; no
  milestone models it; both mapping strategies declare it as a limitation.
- **Ventilation, decoupling and the ventilator.** (b5) and (b6) reach a number
  only once the machine owns the ventilator, which this abstraction does not
  give it. Ventilation stays a patient-side control, and decoupling is a fourth
  strategy slot opened by whichever milestone moves it.
- **Automated end-tidal control.** Planned-milestone item 5. It fails two of
  this design's three admissibility conditions, which is the reason it is a
  milestone rather than a strategy, and that reason is now recorded rather than
  assumed.
- **Every `unknown` in the survey.** Apparatus volumes, flow floors, agent
  lists and sample flows for the GE and Getinge machines, and for three of the
  five Dräger ones. The survey's last section names the manuals and the route.
  **That is a condition on each profile, not on this abstraction.** A machine
  whose fields are `unknown` is a machine that cannot be added yet, and its
  manual is sought when that machine's profile is built rather than in advance
  (project owner, 2026-09-20). The design is complete without any of them: the
  reference profile is what it runs on meanwhile by construction, not for want
  of evidence.

## Sources

Every source below is cited in `docs/machine-survey.md`, which records the
retrieval route, the depth of reading and the full bibliographic record for
each. They are named here only where this document reasons from them; nothing
here is a new citation, and `docs/machine-survey.md` remains the authority for
all of them.

- Fukuda T, Fukunaga A, Toyooka H. *J Anesth.* 2006;20(4):268–273 — inlet
  position changes $`F_I/F_D`$ at fixed volume, the measurement behind the
  decline recorded above.
- Hendrickx JF, De Cooman S, Deloof T, et al. *Anesth Analg.*
  2001;93(2):391–395 — cassette-vaporizer output against dial across flow.
- Johnston RV, Andrews JJ, Deyo DJ, et al. *Anesth Analg.* 1994;79(3):548–552 —
  the Tec 6 characterised from 1% to 18%, the provenance of the 18.
- Meyer J-U, Kullik G, Wruck N, Kück K, Manigel J. In: Schüttler J, Schwilden
  H, eds. *Modern Anesthetics.* Springer; 2008:451–470 — the Zeus's two dosing
  modes, the closed surplus gas valve, the gas module's sample draw, and the
  fixed-volume-percentage principle.
- Shin HW, Yu HN, Bae GE, et al. *BMC Anesthesiol.* 2017;17(1):10 — the three
  Dräger apparatus volumes, and machines indistinguishable on volume differing
  significantly in time to target.
- Targ AG, Yasuda N, Eger EI II. *Anesth Analg.* 1989;69(2):218–225 — the
  measured 9.86 L the reference profile's own provenance note reasons against.
