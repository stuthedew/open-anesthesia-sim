---
id: PL-LS3H
title: docs/MODEL.md models the breathing circuit as a non-absorbing volume, and a held measurement says its components absorb substantially and unequally by agent
status: done
added: 2026-09-13
closed: 2026-09-13
priority: P1
effort: S
classes: science, docs
feature: model-spec-accuracy
touches: docs/MODEL.md, src/anesthesia_sim/core/circuit.py
verify: python3 tools/doc_check.py check && grep -q 'circuit.s own walls absorb agent' docs/MODEL.md
---
**Problem.** `docs/MODEL.md` § "Breathing circuit" models the circuit as an
ideal, well-mixed gas volume: agent enters with fresh gas, leaves with the
exhaust, and the walls do nothing. `BreathingCircuit.advance_fresh_gas()`
solves exactly that. The assumption is stated, but nothing says how large the
error is, and until 2026-09-13 nothing in this project measured it.

**The measurement now held.** Targ AG, Yasuda N, Eger EI II. *Solubility of
I-653, sevoflurane, isoflurane, and halothane in plastics and rubber composing
a conventional anesthetic circuit.* Anesth Analg 1989 Aug;69(2):218-25, PMID
2764290. Supplied by the project owner 2026-09-13 and now in the private
reference corpus; read at full text the same day. Its Table 1 gives plastic/gas
and rubber/gas partition coefficients after 6-9 weeks' equilibration, in the
order I-653, sevoflurane, isoflurane, halothane:

- Y-piece (polypropylene) 6.67, 7.68, 10.6, 19.1
- circuit tube (polyethylene) 16.2, 31.2, 57.9, 128
- reservoir bag (latex) 19.3, 29.1, 48.9, 190
- bellows (black rubber) 10.4, 22.6, 42.9, 199
- endotracheal tube (PVC) 34.7, 68.5, 114, 233
- mask pad (PVC) 51.7, 104, 170, 323

The ranking halothane > isoflurane > sevoflurane > I-653 held at every
equilibration time from 7.5 min to 9 weeks. The paper also measured washin at
0.5, 1 and 2 L/min and washout at 1, 3 and 5 L/min in a real circuit against
the ideal exponential, and reports that I-653's curves lie close to ideal while
the others lag.

**Why it matters here, and why it is not a defect in the model.** The
simplification is defensible - the paper's own conclusion is that absorption
"should not hinder induction of or recovery from anesthesia" for I-653 - but
`CLAUDE.md`'s safety-critical standard requires model limitations to be
*visible* rather than merely true, and this one is now quantified and
citable. A learner watching the inspired curve rise is watching a curve that a
real circuit would not quite produce, and the size of that gap depends on which
agent is loaded, which is exactly the kind of agent-dependent error a
cross-agent comparison should declare.

**Where.** `docs/MODEL.md` § "Breathing circuit" and § "Known limitations".
`src/anesthesia_sim/core/circuit.py`'s module docstring states the ideal
assumption and would carry the pointer.

**Approach, to be decided rather than assumed.** The cheap and probably right
answer is a "Known limitations" entry with the citation, the ranking, and the
statement that the model's inert circuit is most nearly true for desflurane and
least for halothane - no equation change. A wall-absorption term is a much
larger change, is out of the current milestone, and is not obviously wanted for
a teaching simulator; it should not be built on the strength of this item.

**Done when.** `docs/MODEL.md` states the assumption's measured cost with its
citation, and says which agent it favours; or the project records a decision
not to, with the reasoning.

**Closed 2026-09-13, on the project owner's approval of the cheap answer and of
capping it there.** `docs/MODEL.md` "Known limitations" gains a bullet -
absorption of agent by the circuit's own plastics and rubber - and a note below
the list that carries Table 1 in full, the ranking that held at every
equilibration time from 7.5 min to 9 weeks, and the consequence a reader needs:
the inert circuit is most nearly true for desflurane and least for halothane, so
this is an omission whose size depends on which agent is loaded. The note sits
beside the lung-tissue one, which does the same job for the other omitted store.

Two guards against over-reading it, both in the note. The authors' own
conclusion is that the absorption "should not hinder induction of or recovery
from anesthesia" for desflurane, so the simplification is defensible rather than
a defect; and the tabulated coefficients *overstate* the effect over the hours
an anesthetic lasts, because equilibration is nowhere near complete in that
time, which the paper says directly.

`core/circuit.py`'s module docstring says what "ideal" excludes and points here,
so a reader of the equation meets the limitation without opening `docs/MODEL.md`.

**No equation changed, and the item says why not**: a wall term is a second gas
store with its own time constant, no teaching objective in `ROADMAP.md` asks for
one, and the Approach above ruled it out before the evidence arrived rather than
after.

**Done when.** `docs/MODEL.md` states the assumption's measured cost with its
citation and says which agent it favours. Done.
