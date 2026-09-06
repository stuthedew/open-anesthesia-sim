---
id: PL-8GV5
title: Decide whether the model should represent anaesthesia's own effect on cardiac output and regional perfusion, which it currently holds fixed
status: untriaged
added: 2026-09-06
---

**Problem.** Cardiac output and the three perfusion fractions are constants
for the whole of a simulation. Volatile anaesthetics reduce cardiac output and
redistribute regional flow, and the agent being simulated is the cause of that
change, so the model holds fixed exactly the quantities its own subject matter
moves.

**Why it surfaced.** While sourcing the reference patient under `PL-6Q8N`, the
reachable literature on adipose perfusion made the point concretely. Moher and
Carey (J Anim Sci 2002;80:1294-8, PMID 12019618) measured adipose tissue blood
flow by 133-xenon washout and report isoflurane anaesthesia roughly halving it
against rest (1.64 +/- 1.12 against 3.92 +/- 4.22 mL/100 g/min). That is swine
rather than human and is **not** a basis for changing any stored value - it is
recorded here only as the observation that prompted the question.

**Why it matters.** The tissue time constants are `V * lambda / Q`, so a flow
that falls under anaesthesia lengthens the compartment's time constant for as
long as the agent is being given. The direction is against the learner's
intuition, which is what makes it worth deciding deliberately: giving more
agent slows the tissue's own equilibration. `docs/MODEL.md` § "Known
limitations" already records that fat is perfused about twice as fast as the
reachable resting measurement; whether perfusion should also *vary* is a
separate and larger question.

**This is a decision, not a change.** The arguments against are real and may
win. Fidelity should match the learning objective, and a fixed-perfusion
three-compartment model is the thing this simulator is built to teach; adding
a dose-dependent haemodynamic response introduces parameters with weaker
provenance than the ones it would perturb, and breaks the direct comparability
with the Gas Man reference implementation that the whole parameter set exists
to preserve. It is also out of the current milestone.

**Where.** `ROADMAP.md` first - this is planned-milestone scope if it is
anything - then `docs/MODEL.md` § "Known limitations", which should say that
perfusion is held fixed under anaesthesia whatever is decided.

**Done when.** Either `ROADMAP.md` carries one line of intent for a
dose-dependent haemodynamic response, or the decision not to model it is
recorded with its reasoning; and `docs/MODEL.md` names the fixed-perfusion
assumption in "Known limitations" either way.
