---
id: PL-65HT
title: A core/ dataclass numeric field default other than 0 or 1 that appears in no provenance-table value is an unsourced scientific constant, and nothing checks for one
status: untriaged
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
