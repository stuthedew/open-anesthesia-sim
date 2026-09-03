---
id: PL-88GQ
title: State every displayed decimal count as a presentation decision the owner can revise
status: untriaged
feature: presentation-safety
touches: src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md
added: 2026-09-03
---

**Problem.** `docs/MODEL.md` § "Displayed precision" and the comment block at
`app/simulation_view.py:55-96` read as if the two-decimal concentration readout
were *derived* — an output of the splitting-error measurement, settled and
safety-critical to touch. The project owner's account of the decision
(2026-09-03) is that it was not: *"some of my decimal point decisions were
fairly arbitrary. I care about display decimal points in UI."* PL-040 and
PL-74TX (re-decide the two-decimal readout) recorded reasoning around the
choice, but the reasoning bounds what is *permissible* — how many digits the
model can support — and does not uniquely pick two. Within that bound the count
is an interpretability call, and it is the owner's.

The same is true of the counts nothing has argued for at all: `.1f` on the
three flow readouts and on elapsed seconds, and the `:.6f` on the agent-volume
integrals that PL-TG60 (stop printing six decimals of an exhaust integral good
to three) already flags. None of these has a recorded rationale; they are
defaults that hardened into apparent decisions.

**Why it matters.** Two costs, and they pull in the same direction. A future
session reading the current prose will treat the readout as a derived constant
and decline to change it, or will price a routine UI adjustment as a
safety-critical model revision — the owner then cannot exercise a decision that
is theirs. And the display precision that *is* load-bearing becomes
indistinguishable from the display precision that is not: a session cannot tell
from the code which counts encode a claim about model fidelity and which are
formatting. Marking the difference is what lets the first be defended and the
second be changed freely.

Displayed precision remains inside the safety standard — `CLAUDE.md` requires
formatting precision to be justified by model fidelity, input precision and
interpretability, and forbids false precision. Nothing here loosens that. The
change is to say which of the three is doing the work for each value, and to
name the permissible band rather than a single settled number.

**Where.**

- `src/anesthesia_sim/app/simulation_view.py:55-96` —
  `CONCENTRATION_DISPLAY_DECIMALS` and `FLOW_DISPLAY_DECIMALS` and their
  comment blocks.
- `src/anesthesia_sim/app/simulation_view.py:828, 848-853, 884-888` — the
  inline `.1f` and `.6f` format strings that carry no constant and no
  rationale.
- `docs/MODEL.md` § "Displayed precision", around lines 1707-1930.

**Done when.** Each displayed value's decimal count is stated as one of two
kinds, explicitly: a *ceiling* the model imposes (showing more would assert
resolution the method does not have), or a *choice* within that ceiling made
for interpretability. For the concentration readout that means recording the
permissible range the error measurement actually licenses and naming two
decimals as the owner's pick inside it, rather than as its only answer. Every
inline format string either gains a named constant with a one-line reason or is
recorded as arbitrary-and-revisable. A reader can tell, per value, whether
changing the count requires re-deriving anything.

**Depends on.** PL-K9HV (justify the simulation step and the supported ranges
without reference to the readout's decimal count) lands first: while `core/`
derives `MAXIMUM_SIMULATION_STEP_S` and the supported input intervals from the
two-decimal readout, calling that readout freely revisable would be false.

**Related.** PL-TG60 (stop printing six decimals of an exhaust integral good to
three) fixes one instance of this and could be closed alongside it.
