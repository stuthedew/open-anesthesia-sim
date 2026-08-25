---
id: PL-007
title: Make the payload/public-dataclass pattern self-evident in `core/parameters.py`
priority: P2
effort: S
status: ready
classes: docs, refactor
feature: core-boundaries
touches: src/anesthesia_sim/core/parameters.py
added: 2026-08-23
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
