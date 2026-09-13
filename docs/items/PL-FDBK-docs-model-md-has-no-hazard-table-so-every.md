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

## Decided 2026-09-13: build it, in `docs/MODEL.md`; and it is not one piece of work with `PL-8LDF`

**Build it.** ISO 14971:2019 § 5.2 made the analysis of reasonably foreseeable misuse
an explicit documented requirement, promoting it from the 2007 edition's passing
reference, and that is the frame the project owner's stated expectation of off-label
use belongs in: a row with a mechanism and mitigations rather than a stronger
disclaimer. Verified against the standard's change summaries on 2026-09-13.

**It lives in `docs/MODEL.md`, not a new `docs/HAZARDS.md`.** Three reasons, in
order of weight:

- `CLAUDE.md` names `docs/MODEL.md` as *the* authoritative specification for the
  implemented model. A hazard table is a safety claim about that model, and a second
  document holding safety claims is a second document to keep true — which is the
  failure this table exists to catch, arriving in the table's own housing.
- Almost every row's mitigation is already prose in this file, and most rows will
  cite a test named in its own § "Required tests". Intra-document citations are what
  `make doc-check` already reads; cross-document ones are a new class of link.
- The one argument for splitting is length — the file is 5,963 lines — and length is
  the weaker consideration. Splitting the safety argument across two files to shorten
  one of them trades a real hazard (a reader who finds the mitigation and misses the
  hazard, or the reverse) for a navigational convenience.

**`PL-8LDF` is adjacent, not the same work, and combining them would make the table
worse.** `PL-8LDF` (tie MODEL.md's required invariants to named tests) maps
*implementation invariants* to tests: does the code solve the intended equations.
This item maps *ways a reader could be misled* to mitigations and tests: does the
display support a correct reading. That is exactly the verification/validation
separation `.claude/rules/expert-review.md` requires be kept distinct.

Checked against the eighteen invariants rather than assumed: of the five candidate
rows this brief lists — a correct number attributed to the wrong agent, a halted run
read as paused, a clamped setting simulated silently, a value shown finer than the
model resolves, a modelled value read as measured — exactly **one** corresponds to an
existing Required invariant ("a delivered concentration above the agent's vaporizer
maximum is rejected, not clamped"). The other four are presentation hazards the
invariants list does not reach, because every invariant in it is about core numerics
and state. A merged table would carry two kinds of row whose "test" column means two
different things, which is a worse artifact than two tables. They should land near
each other and stay separate.

**Still open, and only this:** the row with no mitigation. `docs/MODEL.md` states that
no displayed value may be read as accurate to its last digit as a prediction about a
patient, and that sentence lives only in a specification a learner will never open.
The interface says "Educational simulation only", which is a *use* disclaimer and not
an *interpretation* one. Whether the interface should carry the interpretation
distinction, and in what words, is editorial and it is a string a learner reads, so it
is the project owner's. Every other row is a citation of prose and tests that already
exist, and needs no decision to write.
