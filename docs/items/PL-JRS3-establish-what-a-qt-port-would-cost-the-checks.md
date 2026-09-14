---
id: PL-JRS3
title: Establish what a Qt port would cost the checks that read theme.py: contrast_check and agent_identity_check would pass silently on a tree they no longer describe
priority: P2
effort: S
status: done
classes: defect, ux
feature: presentation-safety
touches: tools/contrast_check.py, tools/agent_identity_check.py, docs/ARCHITECTURE.md
verify: uv run pytest tests/unit/test_contrast_check.py tests/unit/test_agent_identity_check.py && grep -q 'PL-JRS3' tools/contrast_check.py
added: 2026-09-08
closed: 2026-09-14
---

**Problem.** Establish what a Qt port would cost the checks that read theme.py: contrast_check and agent_identity_check would pass silently on a tree they no longer describe

**Problem, restated.** `tools/contrast_check.py` and
`tools/agent_identity_check.py` both read `src/anesthesia_sim/app/theme.py` and
the Flet control tree around it. They are the two checks standing between this
project and a chart no colour-blind reader can separate — `PL-JX0Z` and the
Brettel projection are what they enforce — and they are wired to a specific
toolkit's constants.

**Why it matters, and why it is filed now rather than during a port.** A Qt
port would leave both checks reading a `theme.py` that no longer describes what
is drawn. They would not fail; they would **pass**, on a tree they no longer
describe, which is exactly the failure mode `PL-20PT` had just been fixed for
and the one `CLAUDE.md` names as a check giving a wrong answer silently. A
port's own test suite would be green while the accessibility floor this project
argued for went unenforced.

This is not an argument against a port. It is the cost of one, and it is
cheaper to know it before `PL-QXSB` is decided than to discover it after
`PL-55DH` looks promising.

**Done when** it is established what each check actually depends on, and
whether the dependency is on the *values* — which survive any toolkit — or on
Flet's control objects, which do not. If the former, say so and the port is
cheaper than it looks. If the latter, the two checks are part of the port's
scope rather than collateral, and `PL-QXSB`'s cost side gains an entry.

## Answered 2026-09-14 by porting the tree and running both checks against it

**The dependency is split, and not the way the question assumed.**
`contrast_check.py` reads *values* and survives; `agent_identity_check.py`
reads Flet's *control objects* and goes silent. One of each, so the port's cost
side gains one entry rather than two.

Measured rather than reasoned: `app/theme.py` and `app/simulation_view.py` were
rewritten on the AST, every Flet property assignment replaced by the PySide6
setter call that supplants it, and both tools run against the result with
`--root`.

| probe | what the port does | `agent_identity_check` | `contrast_check` |
| --- | --- | --- | --- |
| baseline | the shipped Flet tree | pass, 6 controls | pass, 0 errors |
| A | every property write becomes a Qt setter | **fail, wrong reason** | pass, 0 errors |
| B | only enable/hide become setters | **PASS, and asserts a falsehood** | pass, 0 errors |
| C | `SimulationView` moves to its own module | fail, correct message | fail, 68 citations |
| D1 | a new module declares a colour | n/a | **PASS, never measured** |
| D2 | `FAT_COLOR` renamed by the port | n/a | fail, names the constant |

**`contrast_check.py` survives, and its loudness is not luck.** Its whole input
is module-level `NAME = "#RRGGBB"` constants, which no toolkit owns. Removing a
declared colour is loud through `missing` (D2); restructuring the two modules it
reads is loud through `check_citations` (C, 68 unresolved symbols) — the symbol
rule `PL-J7C5` added in v0.4.22 for an unrelated reason, which turns out to be
what catches a decomposition. `PL-B9PY` records that the Qt view is built
decomposed from the start, so C is the certain case rather than a hypothetical.

**Its one hole is additive, and the port opens it.** A colour declared in a
module that is neither `app/theme.py` nor `app/simulation_view.py` is measured
by nothing and missed by nothing: D1 put a selection colour at 1.07:1 on the
panel in a new module and the tool reported `0 errors`.
`check_colors_live_in_the_theme` does not catch it either, inspecting only the
view. **Nothing exploits this today** — checked, no hex constant sits outside
those two files anywhere under `src/` — so it is latent, and the decomposed Qt
view is what creates the modules that open it. Filed as its own item rather
than fixed here, this item being to establish rather than to repair.

**`agent_identity_check.py` does not survive, and its failure is worse than
silence.** Rule 1 reads `self.X.disabled = EXPR` paired with `self.X.visible =
not EXPR`. PySide6 spells both as calls, so `property_writes` returns nothing
and the pairing loop runs zero times. In probe B it printed

    agent-identity: 6 control(s) carry the agent colour, none of them rendered disabled

and exited 0, on a tree where all six are driven by `setEnabled()` with no
paired hide. The sentence is an affirmative claim about a tree the check did
not measure, and a reader cannot tell it from the same sentence earned.

**Whether it goes quiet turns on a choice the port makes incidentally**, which
is why this could not be settled by reading the code alone. Porting the colour
writes as well trips rule 2 (A), and moving the class trips the empty-set guard
(C); both fail loudly. But A's message *misdiagnoses* — it reports that the
writer "never writes" the six controls, when the writer writes all six through
`setStyleSheet`. A loud failure that names the wrong cause sends the port
looking in the wrong place.

**So the answer to this brief's own disjunction is "the latter, for one of the
two".** Rule 1 of `agent_identity_check.py` is inside the port's scope rather
than collateral, and it is the half to port first; `contrast_check.py`'s two
read paths widen to whatever modules the decomposed view declares colours in.
Both are recorded in `docs/ARCHITECTURE.md` § "Developer tooling" and in each
tool's own module docstring.

**What was not established.** Nothing here measures what the ported checks
*should* read — that is the port's design work, not this item's. And the probes
are plausible ports rather than the port: they were generated mechanically from
the shipped tree, so they establish how each check behaves under a given
structural change, not which change `v0.5.1` will actually make.
