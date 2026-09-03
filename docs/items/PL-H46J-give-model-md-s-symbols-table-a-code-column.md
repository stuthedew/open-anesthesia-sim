---
id: PL-H46J
title: Give MODEL.md's Symbols table a Code column naming the expression that denotes each symbol
priority: P2
effort: M
status: ready
classes: docs
feature: core-domain-language
touches: docs/MODEL.md
added: 2026-09-03
verify: python3 tools/doc_check.py check && grep -qF '| Symbol | Meaning | Unit | Code |' docs/MODEL.md
---

**Problem.** `docs/MODEL.md` § "Symbols" defines 21 symbols and says nothing
about where any of them lives in the code. § "Selected method (as implemented)"
maps the other direction — it names `BreathingCircuit.advance_fresh_gas`,
`AgentUptakeSystem._exchange_circuit_and_alveoli`, `TissueGroup.advance`,
`VenousBloodCompartment.advance` and `AlveolarCompartment.apply_blood_uptake` —
so the spec already points at the code for the *method* and not for the
*state*. There is no way to get from $`F_v`$ to the thing that holds it without
reading `core/` and inferring.

**Why it matters, and what this table is not.** The project owner sharpened
the bar on 2026-09-03: a reviewer who knows the standard variables and
equations should follow `core/` **without a lookup table**. So this column is
not a reading aid and must never become one — a reader who needs it means the
code has failed. It is scaffolding: it makes the pass enumerable, and it gives
`PL-FZ6T` something mechanical to check so the naming cannot drift back. The
deliverable is code that reads correctly on its own; this is how that is kept
true over time.

It is a table rather than a rename for a separate reason.

The obvious reading of "make `core/` read like the domain" is to name
identifiers after symbols — $`F_A`$ becomes `f_a`. That is the wrong move here
and the table is what replaces it. Identifiers in this project carry their unit
or kind (`alveolar_ventilation_l_min`, `gas_volume_l`), which
`.claude/rules/core-domain.md` asks for explicitly and which a bare symbol
cannot do; and the compartment object already supplies the subscript, so
$`F_A`$ in code is `alveoli.<accessor>` rather than any single identifier. The
mapping therefore has to be from a symbol to an **expression**, which is
exactly what a table column can hold and a naming convention cannot.

Three things follow from having it, and none is available without it:

- The pass becomes finite and enumerable. "Make `core/` read like the domain"
  is unbounded; "every one of 21 symbols has exactly one denotation in code" is
  a list someone can finish.
- The aliasing collapses by construction. Today $`F_A`$, $`F_v`$ and $`F_i`$ are
  reached through three differently-named accessors; filling one column forces
  the question of why, which is what `PL-9SH6` (one accessor name for the
  partial-pressure-equivalent fraction) then acts on.
- It is checkable. `PL-FZ6T` (the domain checks) asserts that every Code cell
  resolves to a real attribute, so the map cannot rot the way prose does.

**Where.** `docs/MODEL.md` § "Symbols" — a fourth column. Each cell holds the
expression a reader would evaluate, in the form `ClassName.accessor` (for
example `AlveolarCompartment.partial_pressure_fraction`,
`TissueGroup.blood_flow_l_min`, `BreathingCircuit.circuit_volume_l`), or `—`
where the model defines a symbol the code does not materialize. $`F_a`$ is the
worked example of that last case: § "Arterial blood" states it is not an
independent state ($`F_a \equiv F_A`$), so its cell should say so rather than
inventing an attribute.

`PL-212V` (the missing tissue:gas symbol row) adds rows to the same table and
should land with this or immediately before it — a Code column written against
an incomplete symbol list would have to be revisited.

**Sequencing.** This is the first item of the pass. `PL-9SH6` and `PL-3TLK`
(the F_I rename) both change accessor names, so writing the column first and
updating it with them is one pass over the table; writing it after means
writing it twice.

**Done when.** Every row of § "Symbols" carries a Code cell that either names a
resolvable expression or states why the symbol has no denotation, the column is
present for the rows `PL-212V` adds, `make check` passes, and no modelled value
changed.
