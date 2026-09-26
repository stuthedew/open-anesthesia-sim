# Anesthesia machines: the variables that change a simulated result

## What this document is, and what it is not

`ROADMAP.md`'s planned-milestone item 1 commits to a modular anesthesia-machine
abstraction, and `PL-FG9D` designs it. This is the survey that item depends on.
Its question is not *what an anesthesia machine is*. It is the narrower one:
**which of the ways real machines differ actually reach a number this simulator
computes or displays** — today, or once the machine milestone and the
multi-substance patient state land.

It is therefore not an inventory. A specification is here because there is a
stated path from it to a computed or displayed value, and that path is written
down beside it. A specification with no such path is left out, or gets one line
under § "Ruled out" if it is one somebody would otherwise raise again.

**Survey only.** Nothing here changes `src/`, and nothing here is a machine
class, a profile schema or an interlock. Those are `PL-FG9D`'s, and this
document's last section is what it needs: which variables are per-machine
*data* and which are genuinely different *behavior*.

## The headline finding, because it decides the abstraction

**Apparatus volume alone does not explain the measured differences between
machines, and the evidence for that is direct rather than inferred.** Two
results, both in-patient or in-bench measurements of quantities this model
computes:

- Shin et al. measured time to a target sevoflurane concentration on three
  Dräger workstations and computed each one's circuit volume and time constant.
  The Perseus A500 and the Zeus IE came out at 3.3 L and 3.2 L, and 6.6 min
  against 6.4 min at 0.5 L/min fresh gas flow — effectively the same circuit on
  this model's only machine parameter. Their times to target still differed
  significantly. The authors attribute the residue to the position of the fresh
  gas inlet relative to the patient, the presence of a fresh-gas-decoupling
  system, the ventilator drive, and the vaporizer's delivery mode.
- Fukuda et al. moved nothing but the **fresh gas inlet** — from between the
  inspiratory valve and the absorber to between the inspiratory valve and the
  patient — on fixed machines, and the inspired/delivered ratio of isoflurane
  and of sevoflurane rose significantly during low-flow anesthesia. $`F_I/F_D`$
  is the ratio this model's circuit equation *is*, and a machine changed it
  without its volume changing at all.

So a machine profile that is a volume and a set of bounds is falsified by the
data before it is written. That does not mean the profile must carry topology —
it means the abstraction has to decide, explicitly, either to carry it or to
state that machines differing only in topology are indistinguishable in this
model. `PL-WZVZ` is what makes that decision visible: a difference shown on a
curve and attributed to a trade name, when the parameter that produced it is
not in the model at all, is a presentation-safety failure under `CLAUDE.md`'s
clinical-output standard.

## The machines surveyed, and why those

No installed-base or market-share source was reachable from this session (see
§ "How a value gets into this document" below), so "in current clinical use" is
established by proxy, and the proxy is stated rather than hidden: **a machine is
here if it is the subject or comparator of a peer-reviewed study published
between 2006 and 2025**, which is evidence it was in service somewhere and
studied there, **and** if it contributes an axis of variation that the rest of
the set does not already cover.

**The table is a map of the variation, not a list of machines to implement.**
Each row earns its place by contributing an axis the others do not, so the set
as a whole is the range of real behavior a machine profile's schema has to be
able to express. Nothing here commits the project to eight profiles, and a
machine's presence below is not a claim that it will be built. The reference
material follows the same rule: a machine's operator or technical manual is
sought as that machine's profile is built, one at a time, rather than gathered
in bulk ahead of the milestone (project owner, 2026-09-20).

| Machine | In because | Axes it contributes |
| --- | --- | --- |
| Dräger Primus | Kern 2012; Shin 2017; Zumsande 2023 | Piston ventilator; fresh gas decoupling; large apparatus volume |
| Dräger Perseus A500 | Shin 2017; Morimoto 2020 | Turbine (blower) drive; small apparatus volume; inlet close to the patient; no decoupling |
| Dräger Zeus IE | Shin 2017; Candries 2022; Bashraheel 2022 | Direct injection of agent (in-circle *and* out-of-circle modes); automated end-tidal control |
| Dräger Apollo | Lerman 2025 | Piston drive with decoupling, measured against a GE machine in patients |
| Dräger Fabius (GS/Plus) | Biro 1997 (decoupling); Fukuda 2006; Morimoto 2020 | Decoupling-style circle; the fresh-gas-inlet experiment's platform |
| GE Aisys / ADU family | Hendrickx 2001; Jakobsson 2017; Leijonhufvud 2017; Lerman 2025; Hoffmann 2025 | Electronically controlled cassette vaporizer; bellows; automated agent control |
| GE Avance | Kern 2012 | Measured directly against a Primus at neonatal settings |
| Getinge FLOW-i | Jakobsson 2017; Leijonhufvud 2017; Candries 2022; Kalmar 2022 | Injector-type agent delivery; automated gas control with a speed setting |

**What is deliberately absent.** Machines whose current US presence this session
could not evidence at all — Mindray's A-series, Penlon, Spacelabs — are out, not
because they are unimportant but because including them would mean writing rows
no source here can fill. Each is a candidate for the first session that can
reach a manufacturer's technical data.

## How a value gets into this document

The brief for this survey asked that machine behavior be taken from the
manufacturer's operator or technical manual, cited by document and revision.
**That was not possible from this session and the departure is recorded rather
than papered over.** Measured 2026-09-19 by the method
`.claude/rules/citing-sources.md` prescribes: the egress gateway refused
`www.draeger.com`, `www.gehealthcare.com`, `www.iso.org`, `webstore.ansi.org`,
`standards.iteh.ai` and every manual-hosting mirror tried, while
`www.ncbi.nlm.nih.gov`, `link.springer.com`, `doi.org` and `search.worldcat.org`
answered. The three routes that remain are the PubMed MCP server, the project
owner's private reference corpus, and direct identifier checks. So:

1. **A measured quantity is cited to the measurement.** Where a peer-reviewed
   study measured the thing the model uses — an inspired concentration, a time
   to target, a vaporizer's output against its dial — that study is the
   authority, and it is a stronger one than a manual would have been. This is
   `docs/MODEL.md`'s own source hierarchy applied unchanged: a primary
   measurement outranks a specification sheet, and a specification sheet is not
   a measurement.
2. **A figure a paper carries but did not measure is marked as such.** Shin et
   al. print the three Dräger apparatus volumes and cite them onward to sources
   this session could not open. They are recorded here as tier 2 — a secondary
   synthesis — and not as measurements, because that is what they are.
3. **A manufacturer's own technical account is used where one is held, and
   quoted.** The private reference corpus
   (`stuthedew/open-anesthesia-sim-references`) holds *Modern Anesthetics*,
   whose chapter on inhalational dosing technology is written by five Dräger
   authors and describes the vaporizers, the injector, the gas module and the
   Zeus breathing system directly. It is a textbook chapter and therefore
   tier 2, but for *what a device does* — as opposed to what a quantity
   measures — it is the manufacturer speaking, which is the class of source the
   brief asked for.
4. **A standard is named by number, title, edition and date only, and the route
   is stated because it is a weak one.** The texts were not reachable and
   neither were the ISO catalogue pages; the edition and date below come from
   **national adoption records surfaced by a web search**, which this project's
   own rule says is not a source. So this document states what each standard
   *is* and never what a clause requires. Every claim that would need the text
   is marked as a gap.
5. **Anything else is `unknown`.** An unknown apparatus volume is a machine that
   cannot be added yet, not a machine with a plausible apparatus volume.

## The variables

Each entry carries its bucket and, for (a) and (b), the reason it reaches a
number:

- **(a)** changes a number the simulator computes today;
- **(b)** changes a number once planned-milestone item 1 (machine and
  interlocks) and the multi-substance patient state land;
- **(c)** ruled out — collected in one section at the end, with the condition
  under which each stops being ruled out.

### (a1) Apparatus gas volume

**Why it reaches a number.** `circuit_volume_l` is $`V_C`$ in the circuit
equation, so it sets the fresh-gas wash-in time constant
$`\tau_C = V_C/\dot V_F`$ — the part of the early rise in inspired
concentration that belongs to the machine rather than to uptake. It is the
single most-taught point about a circle system and the model already carries it.

**Where it lives today.** `src/anesthesia_sim/data/machines/reference_circle_system.json`,
6.0 L, with its provenance and the deliberate departure from Gas Man's published
8.0 L recorded there (`PL-4YY1`).

**What the survey found.** The apparatus volume of a workstation is roughly half
this figure on the two most recent Dräger designs and roughly equal to it on the
older one, once a disposable patient circuit is added:

| Machine | Apparatus incl. absorber, excl. patient circuit | With a 1.2 L patient circuit | $`\tau_C`$ at 4 L/min |
| --- | --- | --- | --- |
| Dräger Primus | 4.7 L | 5.9 L | 89 s |
| Dräger Perseus A500 | 2.1 L | 3.3 L | 50 s |
| Dräger Zeus IE | 2.0 L | 3.2 L | 48 s |
| GE Aisys / Avance / ADU | unknown | unknown | — |
| Getinge FLOW-i | unknown | unknown | — |
| Dräger Apollo, Fabius | unknown | unknown | — |

The apparatus figures and the 1.2 L circuit are Shin et al.'s, tier 2 as
explained above; the right-hand column is arithmetic on them at this
simulator's own default flow. **So machine choice moves the circuit time
constant by a factor of about 1.8 at any given flow** — which is a visible
difference in the first two minutes of every run.

**One coincidence worth naming, so a later reader does not mistake it for a
justification.** The stored 6.0 L sits within 2% of the Primus-with-circuit
figure of 5.9 L. The 6.0 L was not chosen to represent a Primus — it predates
this survey and was kept on a ruling that the value is not critical — and
nothing here should be read as having sourced it retrospectively.

**A design consequence for `PL-FG9D`.** The model has one well-mixed circuit
compartment, so its $`V_C`$ is apparatus *plus* patient circuit. The patient
circuit is a consumable chosen per case, not a property of the machine. A
machine profile therefore cannot own $`V_C`$ outright: it owns an apparatus
volume, and something else supplies the circuit.

### (a2) Default fresh gas flow

**Why it reaches a number.** It is the flow every run starts at, so it sets
$`\tau_C`$ at $`t = 0`$ and the whole of the accuracy table's default-flow
column. `PL-8DJ7` established that it is a machine setting rather than a patient
or agent property, and the project owner's recorded decision was to wait for
this abstraction.

**Where it lives today.** The same machine data file, at 4.0 L/min, declared in
that file's `provenance_gap` as a **teaching default, not a clinical
recommendation**, with no published counterpart. (The item's brief describes it as a literal in
`src/anesthesia_sim/core/circuit.py`; that stopped being true when `PL-4YY1`
moved both constants into the data file, and the literal that remains is a
default for a bare unit-test construction, guarded by a test that fails if it
disagrees with the file.)

**What the survey found: no machine default, and one recommendation that is not
a survey of practice.** No reachable source states a startup fresh gas flow for
any surveyed machine. What the literature carries is normative rather than
descriptive. Kalmar et al. conclude in those words that *"routine clinical
practice using what historically is called 'low flow anaesthesia' (e.g. 2 L/min
FGF) should be abandoned"* in favour of automated minimal-flow delivery — a
recommendation drawn from a single-centre retrospective of 25 cases per group on
one workstation, not a measurement of what flows are used. What it does
establish about practice is its own comparator: a fixed 2 L/min group the paper
calls conventional low flow, which already sits below this simulator's 4 L/min
default.

**Two papers this section first cited beside it do not support a claim about
practice, and the correction is recorded rather than quietly dropped**
(`PL-NM7X`, 2026-09-20). Candries et al. randomised 0.2 to 6 L/min and Hoffmann
et al. ran 0.3 to 6 L/min, and until 2026-09-20 this section read those two
ranges as establishing that *"4 L/min is at the high end of contemporary
practice rather than the middle of it"*. Neither supports it. Candries' range is
the protocol of a Gas Man validation study, chosen to span a wide envelope;
Hoffmann's is a bench protocol run *in vitro* into a 2 L test lung, whose
settings that paper describes as reflecting clinical conditions and whose range
contains 4, 5 and 6 L/min — so it reads, if anything, the other way. **A study's
chosen flow range is not a report of practice**, which is the error
`reference_circle_system.json`'s De Wolf entry already guards against for its
1 L/min.

**The decision, and what it turned on** (project owner, 2026-09-20, ratified,
over lowering the default to match contemporary low-flow practice). The
simulator keeps 4.0 L/min, relabelled in the data file as a **teaching default,
not a clinical recommendation**. An unlabelled default teaches a norm whatever
number it holds, so moving to 0.5 L/min would relocate the problem rather than
remove it, and would carry the same absent provenance this section objects to,
since no machine publishes a startup flow either. What 4 L/min buys is a
$`\tau_C`$ near 90 s, which makes the machine's own lag a separable phase ahead
of patient uptake inside a run a learner will sit through; at 0.5 L/min it is
about 12 minutes and the demonstration no longer completes. What was wrong was
the sentence, not the number.

### (b1) Delivered concentration is not the dial setting

**Why it reaches a number.** $`F_D`$ enters the circuit equation as the
concentration arriving with fresh gas, and the interface presents it as a set
value a learner maps onto a real dial. A machine whose output differs from its
dial by 20% is delivering a different $`F_D`$ than the model assumes, and the
error is a function of agent, carrier gas and flow — all three of which the
model either has or will have.

**What the survey found.** Two bench characterisations, both tier 1, of the two
device classes that matter:

- **GE's cassette vaporizer (ADU/Aladin family).** Hendrickx et al. measured
  output against dial across the whole range of each agent: within 10% of dial
  at 0.3–10 L/min for isoflurane, within 10% at 0.5–5 L/min for sevoflurane, and
  within 13% at 0.5–1 L/min for desflurane, with larger deviations outside those
  flow ranges. Their conclusion is the one that matters for the abstraction:
  *"Despite a different design and the use of complex algorithms to improve
  accuracy, the same physical factors affecting the performance of conventional
  vaporizers also affect the ADU vaporizer."*
- **The Tec 6 desflurane vaporizer.** Johnston et al. measured eight vaporizers
  and found output highest with oxygen and lowest with nitrous oxide as carrier,
  the effect accentuated at low flow and correlated with carrier gas viscosity.
  At 1.0 L/min and a 10% dial setting: 10.3 ± 0.66 vol% in 100% oxygen,
  9.4 ± 0.58 in air, 8.7 ± 0.52 in 30% oxygen with 70% nitrous oxide, and
  8.1 ± 0.44 in 100% nitrous oxide — the last 19% below the dial.

**And the two device classes do not even deliver the same *kind* of quantity.**
Meyer et al., writing for the manufacturer of one of the surveyed machines,
state it in one sentence: *"The desflurane vaporizer principle described here
delivers a fixed volume percentage, making it different from conventional
vaporizers, which deliver fixed partial pressures."* The same chapter gives the
mechanism behind the carrier-gas effect above independently of Johnston et al.:
*"Desflurane vaporizers are calibrated for operation with an FGF of 100% O2
concentration, resulting in differences between set and actual concentrations
for other FGF mixtures."*

This one is a units question rather than a magnitude question, which puts it
squarely inside `CLAUDE.md`'s clinical-output standard — the correct number
carrying the wrong units is a safety failure, and this model works in partial
pressure fractions throughout (`delivered_partial_pressure_fraction`). A dial
number means a partial pressure on one device class and a volume fraction on
the other, and the two diverge wherever ambient pressure is not one atmosphere.

**What it needs.** The flow-dependence half needs only the machine milestone.
The carrier-gas half needs nitrous oxide in the model, which is planned-milestone
item 6 and the multi-substance state beneath it, so it is bucket (b) rather than
(a) for that reason and no other. The fixed-volume-percentage half needs only a
decision about whether this model claims to hold at one ambient pressure.

### (b2) Vaporizer dial range and maximum, and where that number belongs

**Why it reaches a number.** The dial maximum bounds $`F_D`$ and is enforced in
`src/anesthesia_sim/core/circuit.py` as `max_delivered_partial_pressure_fraction`.

**What the survey found: the maximum is a property of the device, not of the
agent.** The model stores `max_delivered_concentration_percent` per *agent* —
desflurane 18.0, sevoflurane 8.0, isoflurane 5.0. The 18% is the calibrated
maximum of a particular device: Johnston et al. characterised the Tec 6 across
*"all integer dial settings from 1% to 18%"*, and `docs/MODEL.md` already names
that provenance in the breathing-circuit section. A desflurane vaporizer of a
different design, or a machine with an electronically controlled injector, is
not bound to 18% by anything about desflurane. So a machine dimension has to
qualify this field, which is `PL-FG9D`'s parameter/strategy question arriving
with a concrete first case.

**Dial increments: unknown, and deliberately not guessed.** `PL-043` decided to
leave the interface control continuous and recorded that the fidelity argument
*reverses* if real machine simulation is built. The evidence that decision
needs is a per-device increment schedule, and no reachable source supplies one:
Johnston et al.'s integer settings are the grid they *tested*, not a statement
that the dial has integer detents. Recorded as unknown.

### (b3) Delivery mode: bypass vaporizer against direct injection

**Why it reaches a number.** A conventional bypass vaporizer sits in the fresh
gas stream, so the model's $`\dot V_F F_D`$ term describes it. A direct-injection
machine can put agent *into the circle itself*, downstream of the fresh gas
inlet — at which point there is no $`F_D`$ at the inlet to speak of, and the
agent-arrival term is not the same term.

**What the survey found.** The Zeus IE offers both, as separate modes. Meyer et
al. describe the device: a reservoir, a dosing chamber and a heating unit,
injecting liquid agent from a pressurised chamber into a heated vaporising
chamber through a pulsed valve, with the vapour delivered to the breathing
system through a heated pipe. Their account of the two modes is what decides the
modelling:

- **Fresh gas mode.** The user sets a fresh gas agent concentration and the
  vapour is mixed with fresh gas before entering the breathing system — *"In
  this dosing mode the agent dosage performance is equivalent to a conventional
  vaporizer."* So this mode *is* the model's existing term, and needs nothing
  new.
- **Auto control mode.** Delivery to the breathing system is *"independent of
  the FGF settings"*, through a separate inlet, under closed-loop feedback on an
  expiratory target.

Shin et al. measured both and found them to differ from each other, with the
ordering reversing as flow rises: the in-circle mode reached the target faster
at 0.5 and 1 L/min and slower at 3 L/min.

This is the clearest **behavior rather than data** case in the survey. No value
in a profile distinguishes these two; they are different equations. It is also
the tidiest, because the same machine's fresh gas mode is the equation this
model already has — a machine abstraction that gets the mode boundary right
inherits one half of the Zeus for nothing.

### (b4) Automated end-tidal or target control

**Why it reaches a number.** It inverts the control direction. The user sets a
target end-tidal concentration and the machine sets the dial and the flow, so
the simulator's two most-used controls stop being inputs and become the
machine's outputs. It is planned-milestone item 5.

**What the survey found.** The behavior is not a faster version of manual
control and cannot be modelled as one. Shin et al. found the Zeus's automatic
mode reaching about 3.6% very rapidly and then taking a considerable further
delay to settle at 4%, because the controller slows its approach to avoid
overshooting the target — so at 3 L/min the automatic mode was *slower* to
target than the manual one. Kalmar et al. found the FLOW-i's automated gas
control consumes agent as a function of its speed setting (6.0 mL at speed 2 to
7.3 mL at speed 8 over 45 min at a 2% end-tidal target), so even the same
machine in the same mode is not one behavior.

**Two structural facts from Meyer et al.'s description of the Zeus, either of
which on its own decides how this is modelled.**

- **Fresh gas flow stops being an input.** Three feedback loops run in parallel,
  and fresh gas flow is an *output* of two of them: the volume controller's
  *"output control variable … is the amount of FGF, including agent flow"*, set
  from the reservoir bag's filling level to hold the system volume constant; the
  oxygen controller's is *"the oxygen concentration and the amount of FGF"*. The
  agent controller sets injected liquid when the level is low and, when it is
  high, flushes with fresh gas instead. So on an automated machine the
  simulator's two principal controls are not settings at all.
- **The machine runs a patient model of its own.** *"Based on a simplified
  physiological model of the patient, a feedback controller calculates the
  amount of agent from the deviation between the expiratory target value and the
  expiratory concentration."* Simulating such a machine means running a
  controller whose own model differs from this one's, which is a scope decision
  for planned-milestone item 5 and not a parameter.

### (b5) Fresh gas decoupling

**Why it reaches a number.** With decoupling, fresh gas is diverted to the
reservoir bag during inspiration and returned during expiration, so the
delivered tidal volume does not vary with fresh gas flow. Without it, it does.
Ventilation is a patient-side control in this model today, so this reaches no
number *today*; it reaches one the moment the machine milestone gives the
machine a ventilator.

**What the survey found.** Biro measured a circle system with and without a
decoupling device: without it, fresh gas flow and inspiratory duration had a
pronounced influence on the resulting minute volume, statistically significant
above 4 L/min; with it, minute volume was unaffected by either. Decoupling also
changes the *agent* path — Shin et al. name the absence of a decoupling system
as one reason the Perseus reached target fastest, because decoupling routes
fresh gas through the bag before it reaches the circle.

**A mode-awareness hazard worth carrying into the design.** Križmarić et al.
showed that with decoupling, disconnecting the reservoir bag entrains room air
into the breathing circuit. A machine feature that silently changes what is in
the circuit is the kind of hidden mode `.claude/rules/expert-review.md` asks to
be designed against, and it is a candidate scenario for the machine milestone
rather than only a parameter.

### (b6) Ventilator drive

**Why it reaches a number.** Through mixing rate and apparatus volume, not as a
taxonomy. Shin et al. attribute part of the Perseus and Zeus advantage to
blower-driven ventilators *"with rapid mixing"*, against the Primus's classical
piston. Jain and Swaminathan's review is the standard description of the three
families — double-circuit bellows, single-circuit piston, and turbine — and of
which of them decoupling is usually paired with.

**Surveyed for its consequence, per the brief.** The profile field this argues
for is not "piston"; it is whatever quantity mixing rate enters the model as, if
the machine milestone decides to represent it at all.

### (b7) Fresh gas inlet position

**Why it reaches a number.** Directly: it changes $`F_I/F_D`$ at a fixed volume
and a fixed flow, which is the ratio the circuit equation computes. See the
headline finding above.

**What the survey found.** Fukuda et al.'s randomised patient study is the
measurement: moving the inlet from between the inspiratory valve and the
absorber to between the inspiratory valve and the patient significantly raised
the inspired/delivered ratio of both isoflurane and sevoflurane during low-flow
anesthesia, on two decoupling-style machines. Shin et al. rank their three
machines by inlet proximity and use it to explain the residue their volume
calculation could not.

**This is the variable that tests the abstraction's honesty.** A single
well-mixed compartment has no place to put it. Calibrating an "effective volume"
to reproduce the observed kinetics would fit the curves and would be a
fabrication: it would attribute to volume a difference that volume did not
cause, and `PL-WZVZ`'s comparison table would then print a sourced-looking
number that no measurement supports.

### (b8) Flow bounds, minimum oxygen flow, and the hypoxic guard

**Why it reaches a number.** As refusals. The model's supported fresh gas flow
range is declared in `src/anesthesia_sim/core/supported_ranges.py` as 0.0 to
10.0 L/min, which is the *model's* domain of validity, not any machine's
deliverable range. A machine that will not go below its minimum total flow, or
that will not deliver a hypoxic mixture, refuses a setting the model currently
accepts.

**What the survey found: unknown for every machine.** No minimum oxygen flow,
minimum total flow or deliverable range for any surveyed machine was reachable.
The governing standard is **ISO 80601-2-13:2022**, *Medical electrical
equipment — Part 2-13: Particular requirements for basic safety and essential
performance of an anaesthetic workstation*, second edition, 2022-04, amended by
ISO 80601-2-13:2022/Amd 1:2026. **Its text was not reachable and no claim about
what it requires is made here** — naming it is a pointer for the session that
can open it, not a citation of a requirement.

**The structure now exists and the value is still unknown** (2026-09-20,
`PL-8PS6`). A machine profile carries `deliverable_fresh_gas_flow_range`, and
`BreathingCircuit` refuses a flow outside it separately from the model's own
envelope. `reference_circle_system.json` declares `null` on the strength of
this section, so a session that reaches a deliverable range for a real machine
writes it into the profile rather than designing a home for it. The minimum
total flow is that range's floor and is not a second field; the minimum oxygen
flow reaches nothing the model computes until there is a hypoxic guard to
consume it.

### (b9) Which agents a machine can deliver, and the single-agent interlock

**Why it reaches a number.** Model selection is safety-critical under
`CLAUDE.md`'s clinical-output standard. Choosing an agent a machine cannot
mount should be refused rather than simulated, because simulating it attaches a
trade name to a delivery that machine cannot perform.

**What the survey found.** The reason the interlock exists is quantified.
Andrews et al. modelled the consequence of misfilling a conventional vaporizer
with desflurane: the calculated output of a misfilled enflurane vaporizer at a
1% dial setting and 22 °C is 57.8%, or 9.6 MAC, and misfilled enflurane,
isoflurane and halothane vaporizers at one-MAC dial settings compute to 14.0,
10.2 and 7.8 MAC of desflurane respectively. They conclude that safe delivery of
desflurane requires engineering safeguards. That is the design pressure behind
agent-specific filling, standardised as **ISO 5360:2016**, *Anaesthetic
vaporizers — Agent-specific filling systems*, fourth edition, 2016-02-15. A
catalogue abstract for that standard states that dimensions for desflurane are
not specified in it, on the grounds of that agent's properties; **the standard's
text was not read here**, so that sentence is recorded as a lead for the session
that can open it, not as a fact this document establishes.

**So desflurane is not an agent with different numbers; it is its own case**,
and on this the reachable sources agree without needing the standard. It needs a
heated, pressurised, electromechanically coupled delivery device — Andrews and
Johnston's description of the Tec 6 is the primary account, and Meyer et al. give
the working figures: the agent is electrically heated in a sealed chamber to
39 °C, *"creating a pressure of approximately 1,550 mmHg"*, with agent flow cut
off entirely on tilt, power failure, low liquid level, or disagreement between
the two differential pressure sensors. A machine without such a device cannot
deliver desflurane at all, which is a capability question rather than a
parameter.

**Per-machine agent lists: unknown**, and they are exactly the kind of fact a
manufacturer's technical data states plainly.

### (b10) Sidestream sample flow

**Why it reaches a number.** A sidestream gas analyser removes gas from the
circuit continuously. At the flows the literature now uses, that is not a
rounding error: 200 mL/min against a 300 mL/min fresh gas flow is two thirds of
the fresh gas. In the model it is a second loss term in the circuit balance,
which today has only the fresh-gas exhaust.

**What the survey found.** Two figures, and the more useful one is that the loss
may not exist at all. Shin et al. sampled at the Y-piece at 200 mL/min with a
bench analyser and state that *"the gas samples were not returned to the
system"*. Meyer et al., describing the integrated multi-gas module of a surveyed
machine, put the draw at *"a continuous gas flow in the order of 100 ml/min or
more"*, also in a side stream — and name the alternative in the same section: a
**mainstream** sensor sitting between the Y-piece and the tracheal tube, which
measures in place and draws nothing.

So this is a two-valued machine (or monitor) property before it is a rate:
sidestream with the sample scavenged is a loss term, sidestream with the sample
returned is not, and mainstream has no term at all. Per-machine values are
**unknown**; the configuration question is the one to ask first.

### (b11) Whether the circuit exhaust is unconditional

**Why it reaches a number.** It is a term in the conservation identity rather
than a parameter in it. `docs/MODEL.md`'s circuit balance carries an exhaust of
$`\dot V_F F_I`$ that runs whenever fresh gas runs: an equal fresh-gas volume
leaves at the current mixed-circuit concentration, always. That is how a
semi-closed circle behaves, and it is not how every surveyed machine behaves in
every mode.

**What the survey found.** Meyer et al. describe the Zeus's surplus gas valve
venting excess volume to the scavenging system in ordinary operation, and then:
*"In the automatic controlled mode of the Zeus anesthesia machine, the surplus
gas valve can be closed to prevent any loss of gas volume."* A machine running
with that valve closed has no exhaust term, so its circuit is not losing agent
at $`\dot V_F F_I`$ — the whole of which the mass-balance identity and the
`Circuit exhaust` accounting in `docs/MODEL.md` currently assume.

**This is the one entry that reaches an equation rather than a coefficient**,
and it is therefore the one most likely to be mis-implemented as a parameter. A
closed-circuit mode is a different conservation statement, not a machine with a
small exhaust.

## Ruled out

One line each, written once for the whole survey rather than per machine, and
each with the condition that would bring it back. A rule-out that wanted a
paragraph was moved up into bucket (b) instead.

- **Screens, layouts, alarms and alarm limits, menu structure, workflow.** They
  reach no computed quantity; what the *simulator's own* display may imply is
  governed by `CLAUDE.md`'s clinical-output standard and by `PL-WZVZ`, not by
  what a machine's screen looks like. Back if a milestone ever sets out to
  reproduce a specific machine's interface.
- **Pre-use self-test, checkout procedure, calibration and service intervals.**
  They gate whether a machine may be used, not what it delivers once it is. Back
  if a milestone models machine readiness or failure.
- **Cart, mounting, drawers, mobility, mains and battery, pipeline and cylinder
  supply pressures.** No path to a concentration. Back if a milestone models
  supply failure.
- **Scavenging system type.** Downstream of the circuit exhaust, with no
  back-effect on circuit concentration in this model. Back if a milestone
  models circuit pressure or a closed system where the exhaust is not free.
- **Absorbent chemistry** — Compound A, carbon monoxide from desiccated
  absorbent, absorbent dust. Real and safety-relevant, and this model carries no
  chemistry at all: agent is conserved, never consumed or transformed. Back the
  moment any milestone adds a reaction. The absorbent canister's *volume* is not
  ruled out — it is inside the apparatus volumes in (a1).
- **Circuit component absorption of agent.** Measured, and already recorded as a
  known limitation of the model's inert circuit walls (`PL-LS3H`); it is a
  property of the disposable circuit rather than of the machine, so it is out of
  *this* survey's scope rather than out of the model's concerns.
- **Data export, record-keeping and network integration.** No path to a value.

## What `PL-FG9D` needs: data against behavior

The line falls in a specific place, and the evidence rather than taste puts it
there.

**Per-machine data — a field in a validated, versioned file:**

| Field | Bucket | Status |
| --- | --- | --- |
| Apparatus gas volume, including absorber, excluding the patient circuit | (a1) | Known for three Dräger machines, tier 2; unknown elsewhere |
| Deliverable total fresh gas flow range | (b8) | Unknown for every machine |
| Minimum total flow and minimum oxygen flow | (b8) | Unknown for every machine |
| Agents the machine can deliver | (b9) | Unknown for every machine |
| Per-agent dial maximum, qualified by the delivery device | (b2) | Tec 6 desflurane 18%; otherwise unknown |
| Sidestream sample flow, and whether the sample returns | (b10) | Unknown for every machine |
| Default fresh gas flow | (a2) | No machine publishes one |

**Genuinely different behavior — a code-side strategy chosen from a closed set,
because no value in a file expresses it:**

- **Whether the circuit exhaust runs at all** (b11). A closed mode with the
  surplus valve shut is a different conservation statement, not a small
  exhaust. This one changes `docs/MODEL.md`'s mass-balance identity and should
  be settled before any code is written, because it is the one an
  implementation will otherwise quietly represent as a coefficient.
- **Where agent enters the circle** (b3). Bypass into the fresh gas stream, or
  direct injection into the circle independent of fresh gas flow. Different
  equations, and the Zeus has both — its fresh gas mode being, on the
  manufacturer's own description, equivalent to a conventional vaporizer.
- **Who holds the control loop** (b4). A manually dialled machine takes $`F_D`$
  and $`\dot V_F`$ as inputs; an automated one produces both as the outputs of
  parallel feedback controllers, one of which runs a simplified patient model of
  its own.
- **How the dial maps to delivered concentration** (b1). A function of agent,
  carrier gas and flow, characterised per device class rather than tabulated —
  and one device class delivers a fixed volume percentage where the other
  delivers a fixed partial pressure, so the mapping is not even into the same
  units.
- **Whether fresh gas is decoupled from the tidal volume** (b5), once the
  machine owns ventilation.

**Neither, and this is the finding to decide rather than to discover during
implementation:**

- **Fresh gas inlet position and internal topology** (b7) measurably change
  $`F_I/F_D`$ and have nowhere to go in a single well-mixed compartment.
  `PL-FG9D` has three options and should take one on the record: represent it
  (a multi-compartment circuit — `ROADMAP.md`'s planned-milestone item 39 is the
  nearest existing line of intent), decline to represent it and say so where a
  machine is chosen, or fold it into an effective volume. **The third is the one
  to refuse**: it would make `PL-WZVZ`'s comparison table attribute a real
  difference to a parameter that did not cause it, which is the failure that
  table exists to prevent.
- **Ventilator drive** (b6) has the same shape at lower stakes: it matters
  through mixing, and mixing is not in this model either.

## What is missing, and how the next session gets it

Every `unknown` above is unknown for the same reason, and the fix is one thing:
**a session that can reach manufacturer technical data, or a project owner who
can supply it.** The private reference corpus is the route that worked here and
should be tried first — it answered the vaporizer, injector, gas-module and
closed-circuit questions outright.

**Each of these is sought one at a time, when a profile needs it**, rather than
gathered in bulk ahead of the milestone (project owner, 2026-09-20). The list
below is a lookup table, not a shopping list: an `unknown` is closed at the
moment some machine profile has to carry the field behind it, and that
machine's manual is requested then. No `unknown` here blocks the machine
abstraction, and acquiring all of them in advance of any profile is work nobody
has asked for. Where to look, named so nobody has to rediscover it:

- Dräger *Instructions for Use* for the Perseus A500, Primus, Apollo, Fabius and
  Zeus IE — technical data sections, for apparatus volume, flow ranges, minimum
  oxygen flow and sample gas flow. The Perseus IfU was located at
  `draeger.com/Content/Documents/Content/IfU_Perseus_A500_SW_1.1n_EN_9054101.pdf`
  and refused by this environment's egress policy, not missing.
- GE *User's Reference Manual* for the Aisys CS², Avance and Carestation
  families, and the Aladin cassette's specification, for the same fields.
- Getinge *User's Manual* for the FLOW-i, for the same fields and for the
  volume reflector's contribution to apparatus volume.
- **ISO 80601-2-13:2022** (second edition, 2022-04) and its Amendment 1:2026,
  for what a workstation must guarantee about oxygen concentration and flow —
  the one place this document names a standard and declines to say what it
  requires.
- **ISO 5360:2016** (fourth edition, 2016-02-15), for agent-specific filling and
  the desflurane exclusion.

`PL-WZVZ`'s comparison table takes its rows from this document, so each row it
prints as `unknown` is a row this list is the route to filling.

## Sources

**Route and depth, per `.claude/rules/citing-sources.md`.** Every article below
was retrieved through the PubMed MCP server on 2026-09-19 and its bibliographic
record — PMID, DOI, journal, volume, issue and pages — read there rather than
from a search summary; each entry's DOI links the original. The depth of reading
is stated on each entry, because the abstract is as far as that route goes for a
paywalled article: **full text read**, **abstract read**, or **metadata only**.
One source was read at full text from the project owner's private reference
corpus and says so.

**Measurements of quantities this model computes (tier 1).**

- Fukuda T, Fukunaga A, Toyooka H. Site of fresh gas inlet and ratios of the
  delivered fraction and inspired fraction of inhaled isoflurane and sevoflurane
  in low-flow anesthesia. *J Anesth.* 2006;20(4):268–273.
  PMID 17072690; [DOI 10.1007/s00540-006-0417-6](https://doi.org/10.1007/s00540-006-0417-6).
  Abstract read.
- Hendrickx JF, De Cooman S, Deloof T, Vandeput D, Coddens J, De Wolf AM. The
  ADU vaporizing unit: a new vaporizer. *Anesth Analg.* 2001;93(2):391–395.
  PMID 11473867; [DOI 10.1097/00000539-200108000-00031](https://doi.org/10.1097/00000539-200108000-00031).
  Abstract read.
- Johnston RV, Andrews JJ, Deyo DJ, Trahan LA, Savrick MD, Grady JJ, Prough DS.
  The effects of carrier gas composition on the performance of the Tec 6
  desflurane vaporizer. *Anesth Analg.* 1994;79(3):548–552.
  PMID 8067562; [DOI 10.1213/00000539-199409000-00025](https://doi.org/10.1213/00000539-199409000-00025).
  Abstract read.
- Kern D, Larcher C, Basset B, Alacoque X, Fesseau R, Samii K, Minville V,
  Fourcade O. Inside anesthesia breathing circuits: time to reach a set
  sevoflurane concentration in toddlers and newborns: simulation using a test
  lung. *Anesth Analg.* 2012;115(2):310–314.
  PMID 22584556; [DOI 10.1213/ANE.0b013e318257570f](https://doi.org/10.1213/ANE.0b013e318257570f).
  Abstract read.
- Lerman J, Correa AMR. Sevoflurane washin with the Dräger Apollo and GE Datex
  Ohmeda Aisys workstations in healthy children. *Paediatr Anaesth.*
  2025;35(7):535–541. PMID 40178391; [DOI 10.1111/pan.15106](https://doi.org/10.1111/pan.15106).
  Abstract read.
- Morimoto Y, Shiramoto H, Shimamoto Y. Perseus A500 enables faster recovery
  from desflurane general anesthesia. *J Anesth.* 2020;34(2):281–285.
  PMID 32020373; [DOI 10.1007/s00540-020-02740-8](https://doi.org/10.1007/s00540-020-02740-8).
  Abstract read.
- Shin HW, Yu HN, Bae GE, Huh H, Park JY, Kim JY. The effect of fresh gas flow
  rate and type of anesthesia machine on time to reach target sevoflurane
  concentration. *BMC Anesthesiol.* 2017;17(1):10.
  PMID 28103806; [DOI 10.1186/s12871-016-0294-y](https://doi.org/10.1186/s12871-016-0294-y).
  **Full text read** (PMC5248460). Carries the three Dräger apparatus volumes
  with onward citations this session could not reach; those figures are tier 2
  here, while its times to target are its own measurement.
- Biro P. [The effect of fresh-gas decoupling on respiratory volume. Dräger
  Sulla 808V anesthesia ventilator]. *Anaesthesist.* 1997;46(11):949–952.
  PMID 9490582; [DOI 10.1007/s001010050491](https://doi.org/10.1007/s001010050491).
  English abstract read; article in German.

**Model-relevant behavior and machine description (tier 2, or device
description).**

- Andrews JJ, Johnston RV. The new Tec 6 desflurane vaporizer. *Anesth Analg.*
  1993;76(6):1338–1341.
  PMID 8498675; [DOI 10.1213/00000539-199376060-00027](https://doi.org/10.1213/00000539-199376060-00027).
  Abstract read.
- Andrews JJ, Johnston RV, Kramer GC. Consequences of misfilling contemporary
  vaporizers with desflurane. *Can J Anaesth.* 1993;40(1):71–76.
  PMID 8425247; [DOI 10.1007/BF03009323](https://doi.org/10.1007/BF03009323). Abstract read;
  its figures are a mathematical model's output, not a measurement.
- Candries E, De Wolf AM, Hendrickx JFA. Prospective validation of Gas Man
  simulations of sevoflurane in O2/air over a wide fresh gas flow range. *J Clin
  Monit Comput.* 2022;36(6):1881–1890.
  PMID 35318567; [DOI 10.1007/s10877-022-00842-0](https://doi.org/10.1007/s10877-022-00842-0).
  Abstract read; identifiers and the 0.2–6 L/min protocol range re-confirmed
  against the PubMed record 2026-09-20 (`PL-NM7X`). No PubMed Central full text,
  and a check of the private reference corpus the same day did not find it.
  Directly relevant to this project: it validates the reference
  implementation this simulator is compared against, on two workstations, and
  reports materially worse agreement during wash-in than during maintenance.
  Its flow range is a protocol, not a report of practice — see § "(a2)".
- Hendrickx JFA, De Wolf AM. The anesthesia workstation: quo vadis? *Anesth
  Analg.* 2018;127(3):671–675.
  PMID 29239956; [DOI 10.1213/ANE.0000000000002688](https://doi.org/10.1213/ANE.0000000000002688).
  Metadata only; the full text was not reachable. Named here as the review a
  later session should read first, not cited for any figure.
- Jain RK, Swaminathan S. Anaesthesia ventilators. *Indian J Anaesth.*
  2013;57(5):525–532.
  PMID 24249886; [DOI 10.4103/0019-5049.120150](https://doi.org/10.4103/0019-5049.120150).
  Abstract read; open access.
- Meyer J-U, Kullik G, Wruck N, Kück K, Manigel J. Advanced technologies and
  devices for inhalational anesthetic drug dosing. In: Schüttler J, Schwilden H,
  eds. *Modern Anesthetics.* Handbook of Experimental Pharmacology vol. 182.
  Berlin: Springer; 2008:451–470. **Read at full text 2026-09-19 from the
  private reference corpus** (`stuthedew/open-anesthesia-sim-references`,
  section dump `modern_anesthetics/08_Part_IV_Ch5-6_Index`); every passage
  quoted above is from printed pages 453–468, and the page each sits on is
  recoverable from the dump's page markers. Written by Dräger authors, so for
  device description it is the manufacturer's own account; it remains tier 2
  for any measured quantity.
- Kalmar AF, Van Der Vekens N, De Rydt F, Allaert S, Van De Velde M, Mulier J.
  Minimizing sevoflurane wastage by sensible use of automated gas control
  technology in the Flow-i workstation: an economic and ecological assessment.
  *J Clin Monit Comput.* 2022;36(6):1601–1610.
  PMID 34978655; [DOI 10.1007/s10877-021-00803-z](https://doi.org/10.1007/s10877-021-00803-z).
  **Read at full text 2026-09-20** from PubMed Central (PMC9637609) for
  `PL-NM7X`. The sentence quoted in § "(a2)" is the abstract's closing one; the
  body's Conclusion states it again without the parenthesised 2 L/min figure.
  Design bounds what it may be cited for: a retrospective of one centre's
  records, 25 cases per group, on Flow-i workstations alone, comparing AGC
  speed settings against a fixed 2 L/min group and a manual minimal-flow group.
  So it is a recommendation about what practice should be, and evidence that
  2 L/min is the conventional comparator — not a measurement of what flows are
  used.
- Križmarić M, Maver U, Zdravković M, Mekiš D. Effects of the reservoir bag
  disconnection on inspired gases during general anesthesia: a simulator-based
  study. *BMC Anesthesiol.* 2021;21(1):32.
  PMID 33522905; [DOI 10.1186/s12871-021-01256-2](https://doi.org/10.1186/s12871-021-01256-2).
  Abstract read.

**Evidence a machine was in service and studied, used only for the selection
criterion.**

- Bashraheel MK, Eerlings SA, De Wolf AM, et al. Memsorb, a novel CO2 removal
  device part I: in vitro performance with the Zeus IE. *J Clin Monit Comput.*
  2022;36(6):1591–1600.
  PMID 35089526; [DOI 10.1007/s10877-021-00802-0](https://doi.org/10.1007/s10877-021-00802-0).
- Hoffmann M, Jouwena J, De Wolf AM, Carette R, Lauwers RSH, Hendrickx JFA. In
  vitro performance of a charcoal-capturing device with desflurane.
  *Anesthesiology.* 2025;142(6):1038–1046.
  PMID 40073301; [DOI 10.1097/ALN.0000000000005445](https://doi.org/10.1097/ALN.0000000000005445).
  Abstract read; identifiers and the 0.3–6 L/min bench protocol re-confirmed
  against the PubMed record 2026-09-20 (`PL-NM7X`). No PubMed Central full text,
  and a check of the private reference corpus the same day did not find it. It
  is an *in vitro* study into a 2 L test lung and is **not** evidence about
  clinical practice; § "(a2)" records that it was once cited as such here.
- Jakobsson P, Lindgren M, Jakobsson JG. Wash-in and wash-out of sevoflurane in
  a test-lung model: a comparison between Aisys and FLOW-i. *F1000Res.*
  2017;6:389.
  PMID 28529707; [DOI 10.12688/f1000research.11255.2](https://doi.org/10.12688/f1000research.11255.2).
- Leijonhufvud F, Jöneby F, Jakobsson JG. The impact of fresh gas flow on
  wash-in, wash-out time and gas consumption for sevoflurane and desflurane,
  comparing two anaesthesia machines, a test-lung study. *F1000Res.*
  2017;6:1997.
  PMID 29333245; [DOI 10.12688/f1000research.13064.2](https://doi.org/10.12688/f1000research.13064.2).
- Zumsande S, Thoben C, Dennhardt N, et al. Rebounds of sevoflurane
  concentration during simulated trigger-free pediatric and adult anesthesia.
  *BMC Anesthesiol.* 2023;23(1):196.
  PMID 37291484; [DOI 10.1186/s12871-023-02148-3](https://doi.org/10.1186/s12871-023-02148-3).

**Standards, named by number and edition only; texts not reachable.**

- ISO 80601-2-13:2022, *Medical electrical equipment — Part 2-13: Particular
  requirements for basic safety and essential performance of an anaesthetic
  workstation*, second edition, 2022-04; Amendment 1:2026.
- ISO 5360:2016, *Anaesthetic vaporizers — Agent-specific filling systems*,
  fourth edition, 2016-02-15. The edition and date are those a CSA adoption
  record states for the standard it adopts.

**Neither was read, and the route to both was a web search.** `www.iso.org`,
`webstore.ansi.org` and `standards.iteh.ai` were all refused at the gateway, and
`search.worldcat.org` answered but rate-limited the one query put to it. So
these two entries record identifiers taken from catalogue and adoption records
surfaced by a search, which `.claude/rules/citing-sources.md` is explicit is not
a source. They are here as pointers for a session that can open the texts, and
nothing in this document rests on what either standard requires.
