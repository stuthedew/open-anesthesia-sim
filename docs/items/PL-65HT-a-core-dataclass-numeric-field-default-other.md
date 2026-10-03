---
id: PL-65HT
title: A core/ dataclass numeric field default other than 0 or 1 that appears in no provenance-table value is an unsourced scientific constant, and nothing checks for one
priority: P2
effort: M
status: needs-decision
classes: infra, docs
feature: provenance
touches: tools, tests/unit, Makefile
added: 2026-09-13
---

**Problem.** `PL-4YY1` found `circuit_volume_l: float = 6.0` and
`fresh_gas_flow_l_min: float = 4.0` sitting as `BreathingCircuit` field
defaults, where `tools/doc_check.py`'s `check_provenance` could not see them:
that check walks *data files* in both directions, so a scientific constant that
never entered one is structurally invisible to the only tool built to catch a
missing citation. It moved those two into
`src/anesthesia_sim/data/machines/reference_circle_system.json`. It did not
build the check that would catch the next one, and this is that check.

**The counting, run 2026-09-13 before proposing anything.** `core/` holds
**15** numeric field defaults across its dataclasses. **11 are 0, 0.0 or
`Fraction(1.0)`** — empty state and identity, carrying no science. The other
**four are scientific constants restating a data file**:
`AlveolarCompartment.gas_volume_l = 2.5`,
`AlveolarCompartment.alveolar_ventilation_l_min = 4.0`,
`BreathingCircuit.circuit_volume_l = 6.0` and
`BreathingCircuit.fresh_gas_flow_l_min = 4.0`. So the population this check
governs is four today, two of which `PL-4YY1` has already pinned by test and
two of which are `PL-DJYF`.

**The rule that is decidable, and the two that are not.** Matching the
*identifier* against the provenance table's key paths needs a hand-maintained
mapping — the table says `default_fresh_gas_flow_l_min` where the field says
`fresh_gas_flow_l_min`, and `alveolar_gas_volume_l` where the field says
`gas_volume_l` — which is an allowlist by another name, with upkeep, and
`CLAUDE.md`'s tooling gate weighs that against the passes it saves. Matching
against "any value anywhere under `data/`" is worse than useless: 6.0 is the
vessel-rich tissue volume as well as the circuit volume, so that rule would
pass a circuit constant by matching an unrelated quantity, which is the
authoritative-and-wrong failure `CLAUDE.md` names.

What *is* decidable with no mapping and no allowlist: **a numeric default other
than 0 or 1 must appear in the Selected-value column of `docs/MODEL.md`'s
provenance table.** `check_provenance` already parses that table. All four of
today's constants pass it; a new `dead_space_l = 0.15` would not. It is a
screen rather than a proof — a new constant colliding with an existing table
value passes — and it should say so rather than read as a guarantee, which is
the same split `check_provenance` already runs on.

**Where it cannot live, which is the part to settle first.** `doc_check.py`
runs *without* `uv run`, at the interpreter floor, so that a hook or a bare
checkout can run it; the Makefile says so where it invokes the two.
`tools/core_vocabulary_check.py` is the tool that parses `core/` with `ast`,
and its own comment records that it runs under `uv run` for exactly that
reason. So this check either goes in the vocabulary tool, where provenance is
off-topic, or `doc_check.py` grows an interpreter dependency it was built to
avoid, or it becomes a third tool. That choice is the design work here.

**Why it was not built inside `PL-4YY1`.** The Done-when did not require it,
the item's own text said "consider", and the specific defect it would catch is
already caught for `BreathingCircuit` by
`test_the_bare_circuit_defaults_match_the_shipped_machine_file`, at no tool
surface. What a check buys over that test is the compartment nobody remembers
to pin — which is real, and is why this item exists rather than being dropped.

**Done when.** Either the check exists, wired into `make check`, with its home
and its interpreter floor decided and its screen-not-proof limit stated where a
reader of its output can see it; or the item is closed with the reasoning for
declining it, on the counting above.
**Why it matters.** The population is four constants today and two of them are
unpinned (`PL-DJYF`), so what this check would buy is small and measurable and
what its absence costs is not: a scientific constant that enters `core/` without
passing through a data file is structurally invisible to `check_provenance`,
which walks data files in both directions. The only thing standing between that
and the tree is somebody remembering to look, which is exactly the kind of
guarantee `CLAUDE.md` says to move out of the model and into a script. Against
it, the same file's tooling gate asks whether a check will genuinely run again
and whether upkeep costs more than the passes it saves - and the identifier
mapping this one would need is an allowlist with upkeep. That is why it is a
decision rather than a build, and the counting above is what the decision reads.

**Decision needed.** Is the screen worth building at a governed population of four - and if so, does it live in `tools/core_vocabulary_check.py` (where provenance is off-topic), in `tools/doc_check.py` (which would gain an interpreter dependency it was built to avoid), or in a third tool?

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation). Partly overtaken: the cost side
of the argument has gone, the decision has not.** The brief counts two of the
four governed constants as unpinned, on `PL-DJYF` - which closed 2026-09-13 in
v0.4.22, and `tests/unit/test_alveolar.py:92-94` now asserts
`alveoli.gas_volume_l == patient.alveolar_gas_volume_l` and
`alveoli.alveolar_ventilation_l_min == patient.default_alveolar_ventilation_l_min`.
So all four are held by a named test today, at no tool surface.

The population is unchanged and re-counted: 15 numeric field defaults across
`core/`, 11 of them 0, 0.0 or `Fraction(1.0)`, and the same four otherwise -
`alveolar.py:65`, `:66`, `circuit.py:107`, `:108` - all four appearing in
`docs/MODEL.md`'s Selected-value column. What is left is only the decision:
whether a screen is worth building over a population of four that is already
pinned by test, and if so which of the three homes it takes. Nothing in
`tools/` implements it and no declining closure is written.

## Design round 2026-10-03: counted again, and the home question dissolved

**The population, re-counted on origin/main at v0.5.22.** `core/` holds 12 numeric dataclass field defaults written as literals (15 on 2026-09-13): 9 are 0, 0.0 or `Fraction(1.0)`, and 3 are scientific constants - `alveolar.py:65` `gas_volume_l = 2.5`, `alveolar.py:66` `alveolar_ventilation_l_min = 4.0`, `circuit.py:210` `circuit_volume_l = 6.0`. The fourth, `circuit.py:211` `fresh_gas_flow_l_min`, now defaults to the named constant `TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN` (`circuit.py:49`, 4.0), which an `ast` read of literals does not count and a `dataclasses.fields()` read does. All four values sit in `docs/MODEL.md`'s Selected-value column (`docs/MODEL.md:2573`, `:2581`, `:2583`, `:2584`). In the 24 commits that touched `core/` since the brief was written, no new scientific constant entered a dataclass default: the screen would have fired zero times in three weeks.

**The number that would change the answer.** The screen is worth building only if an unsourced constant is likelier to enter `core/` over the project's horizon than about forty lines of test are worth, with no mapping to maintain. The inflow measured here is zero in three weeks over a population of four, which on its own says decline. The horizon decides it the other way: v0.8.0 (multi-substance, nitrous oxide) and the intravenous agents after it are where new `core/` dataclasses carrying constants arrive, and the brief's structural point stands - `check_provenance` walks data files, so a constant that never enters one is invisible to it however many there are. The screen is worth having before that work, not for the four constants it holds today. No head is `generator: live` on 2026-10-03 (`bin/docket generators`), so `CLAUDE.md`'s pause on new checks does not hold either.

**Recommendation: build the screen as one unit test under `tests/unit/`, not as a tool, which closes the three-home question by removing it.** The test imports every dataclass under `core/`, reads each numeric field default through `dataclasses.fields()`, exempts 0 and 1, and asserts the rest appear in the Selected-value column of `docs/MODEL.md`'s provenance table, read through `tools/doc_check.py`'s existing `_provenance_rows` (`tests/unit/test_contrast_check.py` already imports a `tools/` module the same way). It runs under `pytest` in the project virtualenv, so the interpreter-floor question the brief could not settle does not arise: `doc_check.py` keeps its bare-floor rule, `core_vocabulary_check.py` keeps provenance off-topic, and no third tool with Makefile wiring is built. Reading resolved values rather than source literals also catches a default spelled as a named constant, which the `ast` route misses, as the fourth constant above shows. The failure message states the limit where a reader of the output sees it: a screen rather than a proof, since a new constant equal to an existing table value passes. Cost: one test of about forty lines; upkeep: none beyond the provenance table the project already maintains. The build narrows `touches` to `tests/unit`.

The alternative is to close on the counting - four constants, all pinned by named tests, zero inflow measured. It is defensible today and wrong by v0.8.0, which is why it is not the recommendation; if the owner prefers it, close with the counting above as the reason and re-file when v0.8.0 is scoped.
