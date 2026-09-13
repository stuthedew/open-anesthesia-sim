---
id: PL-WVSK
title: Nothing distinguishes a concentration fraction from a percent at the type level, and two boundaries convert implicitly
status: done
priority: P2
effort: M
classes: refactor
touches: src/anesthesia_sim/core/concentration.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/chart_series.py, src/anesthesia_sim/app/control_timeline.py, src/anesthesia_sim/app/wash_in.py, tests/unit/test_concentration.py, docs/MODEL.md, docs/ARCHITECTURE.md
added: 2026-09-02
closed: 2026-09-13
verify: uv run pytest tests/unit/test_concentration.py -q && uv run python tools/ignore_check.py
---

**Problem.** Every quantity in `core/` is a bare `float` carrying its unit in
the identifier only. Two boundaries convert between fraction and percent
inline: `AgentUptakeSystem.for_agent()` divides `mac_percent` and
`max_delivered_concentration_percent` by 100, and
`_handle_delivered_concentration_change` divides the slider's value by 100.
`SimulationSnapshot` carries `max_delivered_concentration_percent` and
`delivered_concentration_fraction` as adjacent fields, and the delivered
slider reads its `max` from one and its `value` from the other.

**Why it matters.** The runtime guards catch the gross error but not the
middle, where one number is a plausible reading under either convention and
passes every guard in the codebase. `CLAUDE.md`'s safety-critical standard
asks for "unit-aware types or equivalent safeguards where practical" and for
avoiding implicit unit conversions; this is the one place the standard's own
words are not met.

**Measured 2026-09-02, and the audit's example was wrong.** The capture said
`0.5` was "a valid fraction (50%) and a valid percent (0.5%)" passing every
guard. Run against a sevoflurane system, `set_delivered_concentration(0.5)`
is **refused** - the vaporizer maximum is 8%, so the fraction `0.08` caps it
and a percent mistaken for a fraction is caught above that. The confusable
band is therefore bounded above by the agent's own dial maximum, not open.

It is not empty, which is the part that survives. Both
`set_delivered_concentration(0.05)` and `set_delivered_concentration(0.0005)`
are accepted, and they are 5% and 0.05% - two orders of magnitude apart,
clinically a full dial setting against a rounding error, and nothing in the
type system, the guards or the identifier names distinguishes the intent. So
the finding holds at a narrower width than it was first written up as: the
gap is `0` to the vaporizer maximum rather than `0` to `1`.

No defect is known to follow from it today. This is a preventive change, and
that is why it is a decision rather than a fix.

**Where.** `src/anesthesia_sim/core/uptake_system.py` `for_agent()`;
`src/anesthesia_sim/app/simulation_view.py`
`_handle_delivered_concentration_change()`;
`src/anesthesia_sim/app/controller.py` `SimulationSnapshot`.

**Decision needed.** Whether to introduce the distinction, and how far:

1. Boundary only - `typing.NewType` for `Fraction` and `Percent` on the four
   control setters, `AgentParameters` and `SimulationSnapshot`, plus two
   named conversions in one module. Zero runtime cost, enforced by the
   existing strict `mypy` gate, and it converts a review question into a
   check.
2. Whole core, every quantity including volumes, flows and times.
3. Neither - the identifier suffix convention plus the range guards are
   judged sufficient, recorded with the reason.

Option 1 is what the audit recommended, and its timing argument is the part
worth weighing: `PL-DHV7` (express compartment concentrations in MAC
multiples as a display unit) adds a third concentration convention, so this
is cheapest before that lands and most expensive after.

**Done when.** The decision is recorded, and if types are introduced, `mypy`
rejects a percent passed where a fraction is expected in a test asserting it.

**Decided 2026-09-13: option 1, and the scope is set by a count the brief did
not have.** `Fraction` and `Percent` are `NewType`s in a new
`core/concentration.py`, which also owns the factor and the two named
conversions. Option 2 is ruled out on a measurement rather than on effort, and
option 3 on a different count.

**The brief says "two boundaries convert implicitly". There are twelve.**
Counted 2026-09-13 with `grep -rn '/ 100\.0\|\* 100\.0' src/anesthesia_sim/`:

| Module | Crossings | Direction |
| --- | --- | --- |
| `core/uptake_system.py` | 2 | percent → fraction, building a circuit for an agent |
| `core/circuit.py` | 2 | fraction → percent, in the refusal message |
| `app/formatting.py` | 2 | fraction → percent: the readout, and the MAC divisor |
| `app/simulation_view.py` | 4 | both, on the slider and the off-scale notice |
| `app/chart_series.py` | 1 | fraction → percent, on every plotted point |
| `app/wash_in.py` | 1 | percent → fraction, the denominator floor |

Six modules, and **six of the twelve are on the path to a displayed clinical
value** — the readouts, the MAC multiples, the plotted points, and the
delivered-concentration slider in both directions — with two more quoting a
refused dial setting back to the reader. `CLAUDE.md` treats the correct number
under the wrong units as a safety failure in its own right, so twelve
hand-written conversions were twelve chances at one. That is the count option
3 has to survive, and it does not.

**Option 2 is not expensive, it is impossible with this mechanism.** Measured
2026-09-13 under this project's `mypy`: `Fraction(0.5) * 2.0` and `f + f` both
reveal as plain `float`. A `NewType` marks a value where it is *passed* and
never where it is *computed*, so it cannot reach inside the governing
equations at all. Ruling out "whole core, every quantity" therefore costs
nothing and is a fact rather than a judgement.

**What it caught immediately.** `docs/MODEL.md` § "Concentrations" said *"The
interface alone converts between fraction and percent"*, and `core/` had
contradicted that since the agent data files began carrying a MAC — two of the
twelve crossings are in `core/`. Rewritten to state where the arithmetic lives
and the three places it is used.

**The cost, measured rather than estimated, in two passes.** Annotating the
vaporizer boundary alone produced seven `mypy` errors and every one was a real
crossing: four assignments inside `BreathingCircuit`'s own mutators, one where
`AgentUptakeSystem` writes the state vector back, two at the controller.

That version was then widened, because it left an asymmetry a reader would
stop on: `BreathingCircuit.set_circuit_concentration_fraction` taking a
`Fraction` beside `AlveolarCompartment.set_concentration_fraction` taking a
`float`, for one quantity `docs/MODEL.md` § "Concentrations" defines once.
Annotating all four compartment setters cost **three** further errors, all in
one function — `_write_state_vector`, where the nine-element state vector is
written back — so the type now means "a model concentration" everywhere rather
than "the fraction side of a percent crossing" in one class.

Eleven `Fraction(...)` wraps in `core/` in total: four field defaults, three
computed assignments in `circuit.py`'s mutators, four in `_write_state_vector`.
**None in `governing_equations.py` or `matrix_exponential.py`**, so
`.claude/rules/core-domain.md`'s bar — the equation visible rather than buried
under its guards — is untouched. `_write_state_vector` is the one place a
`Fraction` is asserted rather than carried, and its docstring says so: the
state vector is nine bare floats, six of them concentrations, and position is
what separates them.

**The test is a `type: ignore`, not a mypy subprocess**, which is what makes
the Done-when affordable. `tests/` is outside `[tool.mypy] files`, so a
directive there is policed by `tools/ignore_check.py` — already run by `make
check`, already running mypy over `tests/` with `warn_unused_ignores`. Two
directives in `tests/unit/test_concentration.py` mark the refused calls;
reverting one annotation to `float` makes both inert and `ignore_check` exits
1 (verified both ways, 2026-09-13). A second mypy invocation in a unit test
would have bought the same assertion and doubled that run's cost.

**The limits are documented rather than implied**, because reading `Fraction`
as something that validates is how this change could be mistaken for more than
it is: the types are erased at runtime, and they cannot catch a wrong
*magnitude* — `Fraction(0.0005)` and `Fraction(0.05)` both type-check. What is
caught is the missing conversion that produces those two from one dial
reading, and `test_concentration.py` asserts exactly that, at 0.08 — a
sevoflurane dial reading of 0.08% accepted as 8%, inside every runtime guard.

**One trap worth recording.** A comment line beginning `# type:` is parsed as
a PEP 484 type comment, so an explanatory comment that happened to start with
the word "type:" made `mypy` report a syntax error at the following line and
stop checking the file. Reworded; nothing structural.
