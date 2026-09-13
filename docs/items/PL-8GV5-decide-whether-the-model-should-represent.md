---
id: PL-8GV5
title: Decide whether the model should represent anaesthesia's own effect on cardiac output and regional perfusion, which it currently holds fixed
priority: P2
effort: M
status: done
classes: planning, docs
feature: model-spec-accuracy
touches: docs/MODEL.md
added: 2026-09-06
closed: 2026-09-13
verify: grep -qF 'held fixed under' docs/MODEL.md && make doc-check
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

**Decision needed.** Does `ROADMAP.md` carry one line of intent for a
dose-dependent haemodynamic response, or is the decision not to model it
recorded with its reasoning? Either way `docs/MODEL.md` § "Known limitations"
should state that cardiac output and the three perfusion fractions are held
fixed under anaesthesia, which is the half that does not wait on the answer.

**Classed `planning, docs` rather than `science`, and it can be overruled.**
The model carries no pharmacodynamic machinery at all, so fixed perfusion is a
boundary of the whole model rather than an unstated exception inside it, and no
displayed value is wrong today. If the missing "Known limitations" sentence
reads as a scientific-transparency gap rather than as scope documentation, the
class becomes `science` and `docket check` moves it to P1.

**Decided 2026-09-13: do not model it. The decision and its reasoning are
recorded in `docs/MODEL.md` § "Known limitations"; `ROADMAP.md` carries no
line of intent, because a line of intent is a commitment to build a thing
eventually and this is a decision not to.**

The half that did not wait on the answer — `docs/MODEL.md` stating that
cardiac output and the three perfusion fractions are held fixed — is done
either way, and it is now a paragraph rather than the one-word "hemodynamic
response" bullet, because what a reader needs is the consequence for the curve
in front of them: $`\tau_i = V_i\lambda_{i:b}/Q_i`$, so a flow that fell under
anaesthesia would *lengthen* every tissue's equilibration for as long as the
agent was being given, which is against the intuition that more agent means
faster equilibration.

**What decided it was reading the human volunteer data rather than reasoning
from "volatiles depress the myocardium".** Three studies, healthy volunteers,
no surgery, each against its own awake baseline:

- **Weiskopf et al., Anesth Analg 1991;73(2):143-56 (PMID 1854029).**
  Desflurane alone at 0.83, 1.24 and 1.66 MAC in 12 normocapnic men: cardiac
  index **did not change**, although stroke volume index fell and filling
  pressure rose at every concentration.
- **Cahalan et al., Anesth Analg 1991;73(2):157-64 (PMID 1854030,
  doi:10.1213/00000539-199108000-00008).** The **same** volunteers in the same
  crossover, with 60% nitrous oxide carrying 0.5 MAC of the total: cardiac
  index now fell dose-dependently.
- **Malan et al., Anesthesiology 1995;83(5):918-28 (PMID 7486177,
  doi:10.1097/00000542-199511000-00004).** Sevoflurane: cardiac index fell at
  1.0 and 1.5 MAC and **returned to baseline at 2.0 MAC** as systemic vascular
  resistance fell; isoflurane similar; the depression diminished with
  prolonged administration and with spontaneous rather than controlled
  ventilation.

So the *sign* depends on the carrier gas, the dose-response is **not
monotonic**, and the effect moves with time at a fixed dose and with the
ventilation mode. This model has no second gas, no ventilation mode, no
surgical stimulus and no pharmacodynamic layer, so the only function it could
carry is a monotonic, time-invariant $`Q(\text{dose})`$ — which is a
relationship the literature above does not show. In a simulator built to
teach, shipping one would be worse than holding the flow fixed and saying so.

That is a stronger argument than the ones the brief anticipated, and it
replaces them rather than joining them. "Fidelity should match the learning
objective" and "it would break Gas Man comparability" are both true and both
would have lost to a good enough dataset; this does not, because there is no
dataset to fit.

**The regional half is weaker still**, which the brief already suspected: the
reachable measurements of how anaesthesia redistributes flow between the
vessel-rich, muscle and fat groups are largely animal — Moher and Carey's
swine adipose washout, which this brief records and which is not a basis for
changing a stored value. `docs/MODEL.md` already carries the finding that the
stored fat flow is about twice Heinonen et al.'s human resting PET
measurement; a *varying* fraction on top of a resting one that far out would
be building a second storey on that.

**What a learner gets instead is the control**, and this is the part that makes
the decision defensible rather than merely cautious. Cardiac output is on the
interface, so the lesson — higher output carries more agent away from the lung,
stores more of it, slows the rise of $`F_A`$ — is reachable by moving it and
watching, which is how the model's own directional gates assert it. What is
missing is only the *automatic* coupling, and `docs/MODEL.md` now tells the
reader to supply that themselves.

**The trigger that would reopen it is recorded rather than the objection
dismissed**: this model gaining a pharmacodynamic layer, or a second gas whose
own haemodynamic profile differs materially from the volatile it accompanies —
nitrous oxide being exactly that case, and `ROADMAP.md`'s planned items 6 and
7.

**Class stays `planning, docs`.** The brief offered to become `science` if the
missing sentence read as a scientific-transparency gap; with the sentence
written, and written as a measured paragraph with its sources, there is no gap
left for the reclassification to describe.
