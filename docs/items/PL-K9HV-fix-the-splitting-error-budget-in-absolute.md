---
id: PL-K9HV
title: Fix the splitting-error budget in absolute units instead of deriving it from the readout
priority: P2
effort: S
status: dropped
reason: superseded by PL-X9KD, which rewrites both target sites wholesale after the exact step lands and has absorbed this item's principle and the owner statement behind it; leaving it open would duplicate that work
classes: refactor, docs
feature: numerical-domain
touches: src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/supported_ranges.py, docs/MODEL.md, tests/unit/test_uptake_system_failure.py
added: 2026-09-03
closed: 2026-09-03
verify: uv run pytest tests/unit/test_supported_ranges.py tests/unit/test_uptake_system_failure.py && grep -q 'def test_displayed_resolution_does_not_bound_the_step' tests/unit/test_uptake_system_failure.py
---

**Problem.** Two `core/` constants are justified *by* the readout's decimal
count rather than in their own units. `MAXIMUM_SIMULATION_STEP_S = 0.1` is
explicitly not where the operator split breaks down — the comment says that is
"two orders of magnitude away" — but "the largest step at which what the
interface shows is still what the model can support", where "what the interface
shows" is the two-decimal concentration readout. `supported_ranges.py` draws its
intervals the same way: cardiac output is capped because beyond it the splitting
error "turns the displayed resolution's 'uncertain by about two counts' into 91
counts, an alveolar readout wrong in its first decimal".

The project owner's statement of intent (2026-09-03): *"some of my decimal point
decisions were fairly arbitrary. I care about display decimal points in UI. I
didn't intend to dictate back end math."* — and the display count is to stay
freely choosable in the range one-to-two decimals.

**Why it matters.** The dependency runs backwards. Numerical accuracy should
bound what may be displayed; here the display choice bounds the integrator step
and the model's supported domain, so a purely presentational move to one decimal
would — by the reasoning as written — license a step roughly ten times larger and
wider input intervals. A second cost is what `supported_ranges.py` appears to
claim: it reads as a statement about where the *model* is valid when it is a
statement about where the *readout* stays truthful at two decimals, and a reader
taking the interval for a physiological validity claim is wrong about what the
guard protects.

**Why no value moves.** PL-74TX (re-decide the two-decimal readout against the
widened splitting-error measurement) already settled the accuracy question in the
direction that makes this item small: at one decimal the readout would be
"uncertain by a fifth of a count even at the extreme". One decimal is therefore
comfortably inside the existing budget, and two decimals is the binding case that
set it. So there is nothing to re-derive — 0.1 s and the present intervals stand.
What is needed is to state the budget those numbers already satisfy as an
absolute quantity and let the readout be checked against it, instead of the
budget being read back out of the readout.

Note the legitimate half, so the fix does not overshoot: choosing a numerical
tolerance from what a user will see is sound practice, and refusing to display
digits the method cannot support is required. What is wrong is that a *chosen*
tolerance is written as a *derivation*, and that nothing else is offered as an
independent statement of either constant.

**Settling the readout does not dissolve this.** The project owner decided on
2026-09-03 that the readout stays at two decimals and one decimal stays
rejected (recorded in PL-88GQ, state every displayed decimal count as a
presentation decision the owner can revise). That closes the display question;
it does not close this one. The defect is the direction of the derivation, not
the count at the end of it — `supported_ranges.py` still appears to state where
the *model* is valid when it states where the *readout* stays truthful, and the
step still moves if the count ever does. A settled input to a backwards
derivation leaves the derivation backwards.

**Where.**

- `src/anesthesia_sim/core/uptake_system.py:40-62` — the comment block above
  `MAXIMUM_SIMULATION_STEP_S` and the "safety-critical change to every displayed
  value" framing that follows from it.
- `src/anesthesia_sim/core/supported_ranges.py:9-39` — the module docstring's
  "Why the model declares these and not the interface" and "Widening any interval
  is a safety-critical change" paragraphs.
- `docs/MODEL.md` §§ "Supported simulation step", "Supported input ranges",
  "Displayed precision" — currently a mutually-referring chain, re-cut together.

**Done when.** The splitting-error budget is stated once, in percentage points
absolute over the reachable domain at the shipped step, as a property of the
model; `MAXIMUM_SIMULATION_STEP_S` and the `supported_ranges.py` intervals cite
that budget rather than any decimal count; and `docs/MODEL.md` records that the
budget was set at the two-decimal case, that one decimal sits inside it with
margin, and that moving between one and two decimals therefore changes nothing in
`core/`. A regression test asserts the last part — that the displayed resolution
is not what bounds the step.

**Not-delegable.** Structural rather than a judgment call: `touches` names
`src/anesthesia_sim/core` and `docs/MODEL.md`, which makes the item
non-delegable whatever proves it. The values themselves do not move, so this
does not need the strongest model.

**Sequencing.** Lands before PL-88GQ (state every displayed decimal count as a
presentation decision the owner can revise): that item cannot call the readout
freely revisable while `core/` derives two constants from it.

**Gate placement decided 2026-09-03.** Not admitted to the frozen v0.4.0 gate,
which is clear at 21 of 21. No displayed value is wrong today, so the
`safety`/`science` exception that would let a post-freeze finding reopen a
cleared gate does not apply; it belongs to the next gate, `v0.4.x — core/ reads
like the domain`, which it fits on its own terms.

**Dropped 2026-09-03, superseded rather than declined.** Both target sites
are splitting-error prose: the comment block at `core/uptake_system.py:37-62`
above `MAXIMUM_SIMULATION_STEP_S`, and `core/supported_ranges.py:15-17` — "the
shipped operator split is first order, so its error is `C * dt`". `PL-X9KD`'s
Done-when requires that "no constant survives whose justification named the
splitting error", which rewrites both wholesale, and after `PL-GS5X` there is no
splitting-error budget left to restate in absolute units.

**The principle is not dropped with the item.** `PL-X9KD` now carries it, under
"Absorbed from `PL-K9HV`": the dependency must not run backwards, and the
project owner's statement of 2026-09-03 — *"some of my decimal point decisions
were fairly arbitrary. I care about display decimal points in UI. I didn't
intend to dictate back end math."* — binds whatever bound the exact step turns
out to justify. Reopen this item only if `PL-GS5X` is abandoned and the split
ships on.
