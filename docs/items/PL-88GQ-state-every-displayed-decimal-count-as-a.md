---
id: PL-88GQ
title: State every displayed decimal count as a presentation decision the owner can revise
priority: P2
effort: S
status: ready
classes: docs, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md, tests/unit/test_simulation_view.py
added: 2026-09-03
verify: uv run pytest tests/unit/test_simulation_view.py && grep -q 'def test_concentration_decimals_are_a_choice_within_a_recorded_band' tests/unit/test_simulation_view.py
---

**Problem.** `docs/MODEL.md` § "Displayed precision" and the comment block at
`app/simulation_view.py:55-96` read as if the two-decimal concentration readout
were *derived* — an output of the splitting-error measurement, settled and
safety-critical to touch. The project owner's account of the decision
(2026-09-03) is that it was not: *"some of my decimal point decisions were fairly
arbitrary. I care about display decimal points in UI"* — with the live range
being one or two decimals, not an open field.

The same holds for the counts nothing has argued for at all: `.1f` on the three
flow readouts and on elapsed seconds, and the `:.6f` on the agent-volume
integrals that PL-TG60 (stop printing six decimals of an exhaust integral good to
three) already flags. Those have no recorded rationale; they are defaults that
hardened into apparent decisions.

**Why it matters.** A future session reading the current prose will treat the
readout as a derived constant — either declining to change it, or pricing a
routine presentational adjustment as a safety-critical model revision. Either way
the owner cannot exercise a decision that is theirs. And the display precision
that *is* load-bearing becomes indistinguishable from the display precision that
is not: nothing in the code says which counts encode a claim about model fidelity
and which are formatting. Marking the difference is what lets the first be
defended and the second changed freely.

**What actually constrains the choice, and it is not accuracy.** Worth recording
plainly, because it is the thing a future revisit has to beat. PL-74TX
(re-decide the two-decimal readout) found one decimal accurate enough —
"uncertain by a fifth of a count even at the extreme" — and rejected it on
interpretability instead: at 0.1 percentage points the fat compartment reads
`0.0%` for an entire hour and muscle for its first three to fifteen minutes,
which erases the wash-in the simulator exists to teach. That is a pedagogical
objection, so it is squarely the owner's to keep or overrule; it should be stated
as such rather than folded into the numerical argument beside it.

Displayed precision stays inside the safety standard — `CLAUDE.md` requires
formatting precision to be justified by model fidelity, input precision and
interpretability, and forbids false precision. Nothing here loosens that. The
change is to say which of the three is doing the work for each value.

**Where.**

- `src/anesthesia_sim/app/simulation_view.py:55-96` —
  `CONCENTRATION_DISPLAY_DECIMALS`, `FLOW_DISPLAY_DECIMALS` and their comment
  blocks.
- `src/anesthesia_sim/app/simulation_view.py:828, 848-853, 884-888` — the inline
  `.1f` and `.6f` format strings that carry no constant and no rationale.
- `docs/MODEL.md` § "Displayed precision", around lines 1707-1930.

**Done when.** Each displayed value's decimal count is stated as one of two
kinds, explicitly: a *ceiling* the model imposes, or a *choice* within that
ceiling made for interpretability. For the concentration readout that means
recording one-and-two decimals as the band the error budget licenses, naming two
as the owner's pick inside it per the decision above, and naming the
`0.0%`-for-an-hour objection as the interpretability reason rather than an
accuracy one. Every inline format string
either gains a named constant with a one-line reason or is recorded as
arbitrary-and-revisable. A reader can tell, per value, whether changing the count
requires re-deriving anything.

**Decided 2026-09-03: the concentration readout stays at two decimals, and one
decimal stays rejected on pedagogical grounds.** The project owner's call, made
once the constraint was shown to be interpretability rather than accuracy. So
this item records a decision rather than reopening one: the band the error
budget licenses is one-to-two decimals, two is the chosen count, and the reason
one is not taken is that the fat compartment would read `0.0%` for an entire
hour and muscle for its first three to fifteen minutes — which erases the
wash-in the simulator exists to teach. Written down as a teaching judgment,
explicitly not as a numerical limit, so a future revisit knows exactly what it
has to beat and does not mistake it for a model constraint it cannot touch.

**Out of scope.** Varying the decimal count per compartment. `docs/MODEL.md`
already rejects it — different counts across the six tiles would put different
magnitudes at the same apparent resolution, and would give the smallest values
the most decimal places. This item records the existing decision; it does not
reopen it.

**Depends on.** PL-K9HV (fix the splitting-error budget in absolute units instead
of deriving it from the readout) lands first: while `core/` derives
`MAXIMUM_SIMULATION_STEP_S` and the supported intervals from the two-decimal
readout, calling that readout freely revisable would be false.

**Related.** PL-TG60 (stop printing six decimals of an exhaust integral good to
three) fixes one instance of this and could be closed alongside it.
