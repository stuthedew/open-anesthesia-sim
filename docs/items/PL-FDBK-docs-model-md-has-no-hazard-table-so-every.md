---
id: PL-FDBK
title: docs/MODEL.md has no hazard table, so every mitigation is argued forward and none is checked backward
status: needs-decision
priority: P2
effort: M
classes: docs
touches: docs/MODEL.md
added: 2026-09-02
---

**Problem.** Every safety argument in this repository runs one way: here is
a decision, here is why it is sound. Nothing runs the other way: here is a
way a reader could be misled, here is what stops it, here is the test that
holds the stop. There is no hazard list.

**Why it matters.** The asymmetry has a measurable cost. Two findings from
the same audit - `PL-VYXP` (the mass-balance baseline anchored to an
implicit zero) and `PL-B32L` (I/O exceptions escaping `core/`'s documented
hierarchy) - are both holes in guarantees the code states about itself, and
neither had surfaced across roughly two hundred queue items, because the
queue records decisions taken rather than harms not yet excluded. A hazard
list is the artifact that finds that class systematically.

ISO 14971:2019 promoted "reasonably foreseeable misuse" from a note in the
2007 edition to a defined term inside the scope of risk analysis, which is
the frame the owner's stated expectation of off-label use belongs in - as a
row with a mechanism and mitigations, not as a stronger disclaimer.

**Where.** `docs/MODEL.md`, or a new `docs/HAZARDS.md`.

**Decision needed.** Whether to build it, and where it lives. Most rows
already exist as prose and as passing tests, so the table would largely be
citations: a correct number attributed to the wrong agent, a halted run read
as paused, a clamped setting simulated silently, a value shown finer than
the model resolves, a modelled value read as measured.

The row that has no mitigation is the one worth deciding on its own.
`docs/MODEL.md` states that no displayed value may be read as accurate to
its last digit as a prediction about a patient, and that sentence exists
only in a specification a learner will never open; the interface says
"Educational simulation only", which is a *use* disclaimer and not an
*interpretation* one. Whether the interface should carry the distinction,
and in what words, is an editorial judgment the audit deliberately did not
make.

Related: `PL-8LDF` (tie MODEL.md's required invariants to named tests)
reaches the same place from the other direction, and the two may be one
piece of work.

**Done when.** The decision is recorded, and if the table is written, every
row names a test or says explicitly that it has none.
