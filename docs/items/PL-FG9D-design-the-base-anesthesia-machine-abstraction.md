---
id: PL-FG9D
title: Design the base anesthesia-machine abstraction so a real commercial machine is a data-plus-plugin addition
priority: P2
effort: M
classes: docs
blocked-by: PL-4DCG
status: blocked
feature: anesthesia-machine
touches: docs/MODEL.md, ROADMAP.md
added: 2026-09-02
---

**Problem.** `ROADMAP.md` planned-milestone item 1 says "a modular
anesthesia-machine abstraction" and stops there. It does not say what a module
*is*, what a new machine costs to add, or what the base type owns versus what
each machine supplies. Today the machine is implicit: `BreathingCircuit` holds
a circuit volume, the vaporizer exists only as a maximum delivered
concentration in the agent data file, and there is no object that means "the
machine". Deciding this after two machines are already in the tree is deciding
it badly, because the second machine is always the one that fits.

**Why it matters.** The goal — a real commercial machine added as a module —
is a fidelity claim, and the abstraction is what makes that claim honest or
not. Two ways it goes wrong, both safety-relevant under `CLAUDE.md`'s
clinical-output standard rather than merely inconvenient:

- **Too permissive.** If a machine module can supply arbitrary behavior, each
  machine becomes bespoke code carrying its own calculation path, and the
  claim that all of them run the same validated model stops being checkable.
- **Too shallow.** If a machine is only a bag of numbers, then a machine whose
  vaporizer is a fundamentally different device is represented as a
  variable-bypass one with different numbers, and the interface will show a
  trade name attached to behavior that machine does not have.

The second is the one to watch, because it looks like it works. PL-043
(continuous vaporizer dial) recorded exactly this trade-off in the other
direction and left an explicit hook: its accepted-cost note says the fidelity
argument *reverses* if real machine simulation is ever built. This item is
where that reversal gets decided.

**Depends on PL-4DCG** (survey of the machines in current clinical use for
the variables that change a simulated result). The extension points are the
axes of real variation that reach a number; designing them before the survey
is guessing, and designing them from variation that reaches no number is worse
than guessing. Machine specifications with no path to a computed or displayed
value are out of scope for the abstraction entirely — they are not modelled,
not parameterised, and not recorded.

**The design questions to answer.** Answer each one explicitly, with the
reasoning recorded, rather than letting the first implementation settle it:

1. **The parameter/strategy line.** Which axes are per-machine *data* in a
   validated, versioned file — circuit and absorber volume, dial ranges,
   minimum oxygen flow, which agents the machine accepts — and which are
   genuinely different *behavior* needing a code-side strategy chosen from a
   closed set. `CLAUDE.md` already forbids executable equations in data files,
   so "put it in the data file" is not available as an escape for the second
   kind. This question has a client waiting: `PL-8DJ7` closed on the project
   owner's decision that the default fresh gas flow is a machine setting and
   should wait for this abstraction rather than be filed under the reference
   patient, so it stays an unprovenanced literal in `core/circuit.py` until
   this design says which file it goes in.
2. **What keeps the machine profile small.** The profile is the per-machine
   data record, and the failure mode to design against is one field per line
   of the manual — every specification tracked because it was available, none
   of them because anything reads it. So the admission rule: a field exists
   only if something in the model consumes it, and the field carries, in the
   schema, what consumes it and what it changes. A field no one can say that
   about is not added.

   The testable form of the same rule, and the one to design toward: **adding
   a machine should add a row, not a column.** Once the abstraction is right,
   a new machine is values for fields that already exist. A machine that needs
   a *new field* is a design event — either the survey missed a real axis, or
   the field is machine trivia that does not belong in the profile — and
   either way it is a decision someone makes, not a data entry someone
   performs. This is question 7 measured from the other end.
3. **How a machine composes with the existing core.** `AgentUptakeSystem` owns
   the four compartments and `circuit` is already machine equipment. Does a
   machine *contain* the circuit, *configure* it, or sit beside it as a
   delivery source? This decides whether adding machines touches the validated
   uptake path at all — and it should not.
4. **Validation and provenance per machine.** What a module must carry to be
   admissible: cited source per constant, a version, and a statement of what
   is *not* modeled. A machine module with no provenance should fail to load
   rather than run.
5. **Naming a real machine in the interface.** What the app may display, given
   that it will model a fraction of that machine's behavior. Options run from
   a full trade name through a generic archetype label ("piston ventilator,
   variable-bypass vaporizer") with the machine named only in an
   about-this-model panel. This is a judgment call about what a learner will
   infer, and it belongs in this item, not in the first module's pull request.
6. **Attributability.** Every difference a machine makes to a curve must be
   traceable to one named parameter with a unit and a source. This is a
   constraint on the design, not only on the display PL-WZVZ builds: if a
   machine can change a result through something with no name — a hidden
   default, a branch inside a strategy — then the difference cannot be
   explained to the user, and the abstraction has put behavior where it does
   not belong. Design so that the parameter set *is* the explanation.
7. **The cost of the second machine.** State it as a target: what a new
   machine takes to add once the abstraction exists — one data file, or a data
   file plus a named strategy from the closed set, and no core change. If the
   design cannot state that, it is not finished.

**Also in scope.** `ROADMAP.md` planned-milestone item 1 says "modular" and
then names one constant (`PL-8DJ7`'s default fresh gas flow). It does not say
what modular is *for* — that a real commercial machine can be added as a
module — which is the goal these items exist to serve. Reword it to state that
goal, and point it at this item, PL-4DCG and PL-WZVZ.

**Scope note.** Design only, recorded as a document. No machine class, no
interlocks, no `src/` change: planned-milestone item 1 remains the
implementation and is still gated behind Phase 1's multi-substance
generalization, since agent switching and residual washout are the behaviors
that make the interlock design meaningful.

**Feeds PL-WZVZ**, which shows a user which parameters differ between two
machines and what each one does. That surface is only buildable if question 6
is answered here.

**Done when.** A design document exists that answers all seven questions above
with reasoning, states the second-machine cost as a concrete target, is
consistent with `docs/MODEL.md`'s existing provenance discipline, and leaves
planned-milestone item 1 scopeable without reopening any of them.
