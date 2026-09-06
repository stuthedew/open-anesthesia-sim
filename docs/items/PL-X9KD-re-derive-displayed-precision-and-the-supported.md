---
id: PL-X9KD
title: Re-derive Displayed precision and the supported step bound, and retire the splitting-error constants, after the exact step lands
priority: P1
effort: M
status: ready
classes: science, safety
feature: numerical-domain
touches: docs/MODEL.md, tests/reference, src/anesthesia_sim/core
added: 2026-09-03
verify: uv run pytest tests/reference/test_coupled_dynamics.py && grep -q 'matrix exponential' docs/MODEL.md
---

**Problem.** Three published statements are derived from the operator split's
error and stop being true the moment `PL-GS5X` lands. Leaving any of them stale
is a safety failure under `CLAUDE.md`'s standard, because each is something a
reader can act on.

1. **§ "Displayed precision"** sets the displayed resolution *from* the
   splitting error, and § "Supported simulation step" states that 0.1 s is the
   largest step at which "every claim Displayed precision makes about the last
   displayed digit stays true". With no splitting error, both derivations are
   void — the constraint becomes input precision and interpretability rather
   than numerical error, which may well justify the same two decimals for a
   different reason. Re-derive; do not assume the answer is unchanged, and do
   not assume it changes.
2. **`MAXIMUM_SIMULATION_STEP_S`** bounds the split's applicability domain, and
   `PL-VP7N` refuses a step outside it. An exact step has no splitting error at
   any step size, so the bound's stated rationale disappears. It does not
   follow that no bound is needed: the compartment capacity guard, the
   scaling-and-squaring headroom, and what a user can meaningfully observe are
   all still real limits. Decide what the bound now means, or remove it and say
   why.
3. **The splitting-error constants** in
   `tests/reference/test_coupled_dynamics.py` lose their referent.
   `SPLITTING_ERROR_BOUND_PER_STEP_SECOND = 2.8e-3` (`:409`) and its three
   consumers (`:793`, `:820`, `:859`) describe a first-order error the exact
   step does not have; `EXACT_SOLUTION_FLOOR = 1e-12` (`:413`) is commented as
   the point "below this the split would no longer be first order because it
   would no longer be a split"; and `MAX_INVERTED_GAP_IN_DISPLAY_COUNTS = 3.0`
   (`:102`) derives itself by multiplying the splitting bound by the shipped
   step. Each needs a new bound derived from the exact step's own error, or
   deletion with the reason recorded — not loosening until it passes.

   **`PINNED_REFERENCE_STATES` is deliberately *not* in this list**, and an
   earlier revision of this item was wrong to put it there (corrected
   2026-09-03). It called them "the split's solution at the historical
   operating point". They are the **independent RK4 oracle's** own solution:
   the comment at `:441-445` says they exist "so that a later edit to the
   oracle or to a parameter file cannot quietly move the reference the shipped
   core is measured against", and
   `test_independent_solution_matches_pinned_reference_states` (`:763`)
   compares the oracle against them at `rel=1e-9, abs=1e-15`. `PL-GS5X` does
   not touch the oracle — `test_oracle_imports_no_solver_from_core` forbids it
   from importing the solver at all — so these states do not move, and
   **re-pinning them from the exact solver would replace an independent
   reference with the shipped solver's own output**, converting the regression
   gate into a self-comparison. That is precisely the failure the paragraph
   below warns against, arrived at from the other direction. Leave them alone.

**Why it matters.** These are the three places where the numerical method
reaches a clinician. A displayed digit justified by an error bound that no
longer exists is false precision with a citation; a step refusal citing a domain
that no longer applies is a wrong error message on a safety path; and an
error bound loosened rather than re-derived converts a regression gate into a
rubber stamp.

**Where.** `docs/MODEL.md` § "Displayed precision", § "Supported simulation
step" and § "Selected method (as implemented)"; `core/uptake_system.py`'s
`MAXIMUM_SIMULATION_STEP_S` and `require_supported_simulation_step`, whose
message and docstring both cite "the operator split's applicability domain", and
`core/simulation.py:38-42`, which repeats the phrase; the comment block at
`core/uptake_system.py:37-62`; `core/supported_ranges.py:14-24` and `:35-39`,
which justify all three maximum input ranges and the three zero floors by the
splitting coefficient `C`; and in
`tests/reference/test_coupled_dynamics.py` the three constants named above —
not `PINNED_REFERENCE_STATES`.

**And four sites in `app/`, added 2026-09-03 after `PL-WB0X` merged (#263).**
That item extracted the formatters into `app/formatting.py`, and carried the
split-derived justification with them rather than leaving it behind. All four
say the two-decimal resolution rests on the shipped operator split's measured
error, and all four are false once the exact step lands:
`app/formatting.py:8-9` (module docstring), `:40-41` (the comment above
`CONCENTRATION_DISPLAY_DECIMALS`), `:62-63` (`format_percent`'s docstring), and
`app/simulation_view.py:65-69`, which names
`core.uptake_system.MAXIMUM_SIMULATION_STEP_S` as "the operator split's
applicability domain". Rewrite each as a citation of the relevant
`docs/MODEL.md` section rather than a restatement of it, so the next
re-derivation reaches one place instead of five.

**Absorbed from `PL-K9HV`** (2026-09-03), which this item supersedes: the
principle that the dependency must not run backwards. `MAXIMUM_SIMULATION_STEP_S`
and `supported_ranges.py`'s intervals are currently justified *by* the readout's
two-decimal count, so a purely presentational move to one decimal would, by the
reasoning as written, license a step ten times larger and wider input intervals.
The project owner's statement of intent, 2026-09-03: *"some of my decimal point
decisions were fairly arbitrary. I care about display decimal points in UI. I
didn't intend to dictate back end math."* Whatever bound the exact step
justifies, it is to be stated in its own units and the display count left free
in the one-to-two decimal range.

**Interacts with `PL-88GQ`** (state every displayed decimal count as a
presentation decision), which is about the same section from the other side; if
both are open, do them together.

**Done when.** Each of the three is re-derived from the exact step's behavior
with the derivation recorded, no constant survives whose justification named the
splitting error or was set by the displayed decimal count,
`PINNED_REFERENCE_STATES` is unchanged and still compared against the oracle
alone, and `make check` passes.

**`PL-GS5X` landed 2026-09-06, and part of this item's ground has been cleared
by it. Read this before starting, so the work is not done twice.**

The line taken was: `PL-GS5X` corrected every statement its own change made
*false*, and left every statement that needs *re-deriving* to this item. So the
document no longer asserts anything untrue, and it no longer asserts the
replacement figures either.

*Already corrected, do not redo:*

- `core/uptake_system.py`'s `MAXIMUM_SIMULATION_STEP_S` comment block and
  `require_supported_simulation_step`'s message and docstring. They no longer
  cite "the operator split's applicability domain"; they say the bound is the
  longest interval settings are held constant over, and that the *value* is
  carried forward rather than re-derived, naming this item. `core/simulation.py`
  repeated the phrase and is corrected too.
- `docs/MODEL.md` § "Supported simulation step": the false opening premise, the
  criterion table and the capacity-guard derivation are replaced by a statement
  of what the bound means now, with the split's coefficients kept as marked
  history. **The value 0.1 s is untouched and its new derivation is still
  owed.**
- § "Selected method (as implemented)" is rewritten around what ships.
- § "Displayed precision" carries a blockquote at its head saying every
  numerical justification below it describes the method that shipped through
  v0.4.2, and naming this item.
- § "What a setting outside the range costs" is re-grounded: the refusal now
  rests on the verification domain and physiological plausibility rather than
  on the displayed number being numerically wrong. Its table is marked history
  and its re-derivation is named as this item's.
- The claim that a gap between two readouts is the least accurate thing on the
  display is **withdrawn** in both places it appeared (§ "Independent-solution
  test" and § "Displayed precision"), because the sequencing bias it described
  was a property of the split.

*Still owed here, unchanged:*

1. § "Displayed precision" re-derived. With solver error gone, what limits the
   resolution is parameter uncertainty, input precision and legibility. Two
   decimals may well survive on the legibility argument alone — but "the finest
   the numerics support" is now false and the four count-figures with it.
2. `MAXIMUM_SIMULATION_STEP_S` re-derived, or removed with the reason recorded.
3. The splitting-error constants in `tests/reference/test_coupled_dynamics.py`.
   `SPLITTING_ERROR_BOUND_PER_STEP_SECOND = 2.8e-3` and its three consumers
   still pass, but only because they are eight orders looser than what the
   exact step achieves; `EXACT_SOLUTION_FLOOR = 1e-12` now makes
   `test_shipped_split_error_is_first_order_in_step` return early on every run,
   so it asserts nothing. `PL-GS5X` added `EXACT_STEP_ORACLE_TOLERANCE = 5e-12`
   and two tests against it — `test_exact_step_matches_the_independent_solution_everywhere`
   and `test_the_disagreement_does_not_shrink_with_the_step` — which is what
   makes the loose ones safe to retire rather than merely stale.
   `MAX_INVERTED_GAP_IN_DISPLAY_COUNTS = 3.0` still derives itself from the
   splitting bound and is untouched.
4. The four `app/` sites, unchanged. `PL-7PLY` targets one of them and should
   be folded in or blocked behind this — see the note on that item.

*One helper name, not on the original list:* `_worst_coefficient_over_phases`
in the same test file divides by the step to report a first-order coefficient.
`PL-GS5X` added `_worst_error_over_phases` beside it for the exact-step gates
and left the original for the tests this item retires; both go together.
