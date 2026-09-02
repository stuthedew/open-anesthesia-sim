---
id: PL-007
title: Make the payload/public-dataclass pattern self-evident in `core/parameters.py`
priority: P2
effort: S
status: done
classes: docs, refactor
feature: core-boundaries
touches: src/anesthesia_sim/core/parameters.py, tests/unit/test_parameters.py
added: 2026-08-23
closed: 2026-09-02
pr: 208
verify: uv run pytest tests/unit/test_parameters.py -k documents_why_it_exists
---

**Problem.** The `_AgentPayload`/`AgentParameters` split — a private
Pydantic validation model paired with a public, frozen,
Pydantic-independent dataclass, repeated for
`_ReferenceAdultPayload`/`ReferenceAdultParameters` — reads as confusing
duplication.
**Why it matters.** The design is correct: it keeps the rest of the core
decoupled from the validation library. But a reader who does not see the
rationale is liable to "simplify" it away.
**Where.** `core/parameters.py`.
**First step.** The module docstring added 2026-08-23 explains the split at
a high level. Decide whether that is sufficient or whether each pair needs
a more local marker — a shared base-naming convention, or a one-line
comment at each `_...Payload` class. PL-021 has since given every payload
model a shared `_StrictPayload` base, so the base-naming half of that
option now exists; what it does not yet carry is why the `_...Payload` /
public-dataclass pair exists at all.
**Done when.** A reader landing on either `_...Payload` class can tell why
it exists without scrolling to the module docstring.

**Decided.** The module docstring is not sufficient — this item's own "Done
when" rules it out by saying a reader must not have to scroll to it. The
rationale went on `_StrictPayload`, which every payload names on its own class
line, so it is one hop from wherever a reader lands rather than 150 lines up.
Each `_...Payload` then carries a one-line docstring saying what it loads and
what it becomes, and the two public dataclasses carry one pointing back, since
the temptation to collapse a pair starts at whichever end you meet first.

**What the explanation turned out to be.** The brief calls the split
"confusing duplication", and the strongest available answer is that it is not
duplication at all — checked rather than asserted before writing it down.
`_AgentPayload` has 8 fields to `AgentParameters`'s 10, `_ReferenceAdultPayload`
10 to `ReferenceAdultParameters`'s 15: the payload mirrors the *file's*
nesting, where three coefficients sit under `tissue_gas_partition_coefficients`
and six values under `tissue_groups`, while the public type is flat and adds
the tissue:blood ratios it derives. The seam functions are that mapping, and
the fields that look copied are the subset where the two shapes happen to
agree. That reframes the pair from "duplication with a justification" to "two
different shapes with a translation between them", which is both true and much
harder to talk yourself into deleting.

The other half is the Pydantic boundary: a payload is a load-time artifact,
discarded by `parse_*_parameters()`, so nothing else in `core/` imports the
validation library.

**Held by a check, not by hope.** `test_every_payload_model_documents_why_it_exists`
walks `_StrictPayload.__subclasses__()` — the same tree the strictness test
walks, for the same reason — and fails on a payload model with no docstring.
Confirmed to fail by stripping one. It deliberately does not check what the
docstring *says*: that is the judgment half, and a check that guessed at it
would be worse than none. Three payload models had no docstring at all before
this (`_TissueGasPartitionCoefficientsPayload`, `_TissueGroupPayload`,
`_TissueGroupsPayload`); they do now, and a seventh added later arrives
explained or fails `make check`.

**Captured, not fixed.** `PL-Y0RZ`: the Pydantic boundary this documentation
now asserts is real today — only `core/parameters.py` imports it — but nothing
enforces it, so a later import into a compartment would leave the prose
claiming a property the tree no longer has. An `ast` walk in `tools/` would
decide it; `tools/contrast_check.py` is the model.

**Doc sweep.** Nothing in `docs/` describes the payload split, so nothing was
made stale. `docs/ARCHITECTURE.md:83` ("validates schema version, required
fields, units, and ranges before constructing `AgentParameters` /
`ReferenceAdultParameters`") and `docs/MODEL.md:766` (tissue:blood coefficients
derived at load time as `AgentParameters` properties) both stay true, and the
second independently corroborates the shape-difference claim above.
