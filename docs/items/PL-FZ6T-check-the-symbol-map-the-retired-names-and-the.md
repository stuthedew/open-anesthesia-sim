---
id: PL-FZ6T
title: Check the symbol map, the retired names and the partition-coefficient rule, so core/ cannot drift back off the domain
priority: P2
effort: M
status: done
classes: infra
feature: core-domain-language
milestone: v0.4.19
touches: tools, tests/unit, Makefile, .github/workflows, docs/ARCHITECTURE.md, docket.toml
blocked-by: PL-9SH6
added: 2026-09-03
closed: 2026-09-13
pr: 532
verify: uv run pytest tests/unit/ && grep -rq 'def test_symbol_code_cell_must_resolve' tests/unit/
---

**Problem.** Everything planned-milestone item 29 establishes is prose the
moment it lands. A later session adding a compartment, an accessor or a
coefficient has nothing telling it the convention exists.

**Why it matters.** `CLAUDE.md` asks for the decidable half of any mechanism to
be moved into code that runs free forever rather than re-derived at full context
in every session, and `tools/doc_check.py` is the project's worked example of
where that line falls: it decides whether a cited path exists, never whether the
sentence around it is still true. The same split applies cleanly here.

**Three rules, all decidable.** Standard library only, so a hook or a bare
checkout can run them; wired into `make check`.

1. **Every Code cell in `docs/MODEL.md` § "Symbols" resolves.** Parse the table,
   parse `core/` with `ast`, and assert each `ClassName.accessor` names a real
   attribute, property or field on that class. Cells reading `—` are accepted
   and must carry the sentence saying why. This is what stops `PL-H46J`'s map
   rotting.
2. **The retired names never reappear in `core/`.** After `PL-9SH6`,
   `concentration_fraction` and the `circuit_`-stuttered form are gone; a closed
   vocabulary check keeps them gone.
3. **A partition-coefficient identifier names both phases, in order.** Any name
   matching `*partition_coefficient` must match
   `<phase>_<phase>_partition_coefficient` with both phases drawn from a
   declared set. This is the rule `PL-212V` establishes, and it is worth
   enforcing precisely because the literature does not hold a convention — Baker
   and Farmery name one symbol "tissue-gas", "tissue-blood" and "blood tissue"
   within a single chapter, so a reader cannot fall back on recall.

**A fourth was considered and is not worth building.** A unit-suffix check over
every float-valued name in `core/` passes today — the suffixes are already
near-universal — so it would be a pure ratchet. That is not disqualifying on its
own, since it stays silent until violated. It is left out because the closed
suffix vocabulary would need maintaining against every legitimate new kind, and
`CLAUDE.md` is explicit that where the benefit is unclear the answer is no.
Reconsider if a suffix regression is ever actually observed.

**What must not be scripted.** Whether a name is the one a reader who knows the
domain would guess. That is the judgment half, it is the whole point of the
pass, and a tool that guessed at it would be worse than no tool because its
output would look authoritative. The three rules above are all mechanical:
resolvable, absent, well-formed.

**Where.** A new `tools/` script, or three rules added to `tools/doc_check.py`
if they sit naturally beside its existing checks — decide by whether the AST
parse of `core/` fits there without distorting it. Tests in
`tests/unit/`, one per rule, each with a fixture that violates it.

**Blocked on `PL-9SH6`** (one accessor name for the partial-pressure-equivalent
fraction), because rule 2 has nothing to check until the rename lands.
`PL-H46J` (the Symbols Code column) was the other blocker and closed
2026-09-13, so rule 1 now has 24 cells to resolve; the `blocked-by` field moved
to the remaining one rather than being cleared, which is the edge this item's
prose had always stated (`PL-KH58`). Rule 3
could be built against `PL-212V` alone if it turns out to be worth splitting.

**Done when.** The three rules run in `make check`, each has a unit test that
fails when its rule is violated, all three pass against the tree, and each
states its rule in a message a reader can act on without opening the script.

**Carry `PL-B667` on this branch** (project owner, 2026-09-13). `PL-B667` is a
one-line correction to `docs/MODEL.md` § "Required invariants", which currently
says derived fractions stay "finite and nonnegative" - the lower bound only -
while `core/` enforces the upper bound of 1 in five places and checks it on
every step's output. It was found while reviewing `PL-9SH6`'s rename.

It belongs here rather than on its own because this item is what makes a spec
sentence enforceable: the corrected invariant is a line a check written here can
read. Landing the sentence without the check is how it drifts again, which is
the failure this whole item exists to prevent.

**Built as `tools/core_vocabulary_check.py`, 2026-09-13.** Three decisions the
brief left open, and what settled each.

**A new script rather than three rules inside `tools/doc_check.py`.** The brief
said to decide by whether the AST parse of `core/` fits there without distorting
it, and it does not: `doc_check.py` is invoked by a bare `python3` in both `make
check` and `.github/workflows/quality.yml`'s floor section, which is the section
that *proves* the standard-library-only promise by running these tools under the
3.11 floor. `core/` targets the version `.python-version` pins, and
`ast.parse`'s `feature_version` only ever narrows the syntax accepted, so a
parse of `core/` cannot run at the floor. The new script therefore joins
`contrast_check.py`, `agent_identity_check.py`, `import_boundary_check.py` and
`workflow_paths_check.py` under `uv run python`, and is deliberately absent from
the floor section for the same reason they are (`PL-Y0RZ`, `PL-L17Q`).

**Rule 3's "in order" is decided by a declared phase ordering, not a closed list
of permitted pairs.** `PHASES` is `("gas", "blood", "tissue")`, read outward
from the gas phase, and an identifier must name the outer phase first — which is
the order the symbol writes, so `tissue_blood_partition_coefficient` is
$`\lambda_{i:b}`$ and cannot be read as its own reciprocal. An ordering was
taken over a list of pairs because it admits a legitimately new pair with no
edit while still refusing every reciprocal; a new *phase* — oil, rubber, soda
lime — is one entry. Whatever precedes the two phases is a qualifier naming
which instance (`fat_tissue_gas_partition_coefficient`) and is unconstrained,
because it says nothing about which phases the ratio is between.

**Rule 2 matches whole identifiers, and two live names are why.**
`require_concentration_fraction` in `core/validation.py` and
`BreathingCircuit.circuit_volume_l` each contain the text of a retired accessor.
Neither is one: the first is the [0, 1] guard every renamed setter calls and is
`PL-6KNM`'s open question, the second is the stutter `PL-9SH6` deliberately left
to `PL-KZS3`. A substring rule would have failed the tree on the day it landed,
over two names nobody has agreed to change, which is the shape of a check that
gets suppressed rather than obeyed. `RETIRED_NAMES` is therefore the transcribed
list from `PL-9SH6`'s table and nothing is inferred from the tree — a name that
has been removed leaves nothing behind to read.

**All three were watched failing against the real tree**, not only against the
suite's synthetic ones: one Symbols cell repointed at `concentration_fraction`,
`AlveolarCompartment.partial_pressure_fraction` renamed back, and
`tissue_blood_partition_coefficient` written as its reciprocal. Each reported
the file, the line and the fix; the second and third tripped rule 1 as well,
which is the Code column doing its job.

**Vacuous passing is an error.** An empty `core/` tree and an unreadable Symbols
table — a renamed heading or a renamed column — are both reported rather than
passed over, because a rule that inspects nothing otherwise reports success
indistinguishable from the real thing.

