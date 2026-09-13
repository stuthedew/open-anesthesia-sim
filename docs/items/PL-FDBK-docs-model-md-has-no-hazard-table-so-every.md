---
id: PL-FDBK
title: docs/MODEL.md has no hazard table, so every mitigation is argued forward and none is checked backward
priority: P2
effort: M
status: done
classes: docs
milestone: v0.4.21
touches: docs/MODEL.md, tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-02
closed: 2026-09-13
pr: 547
verify: python3 tools/doc_check.py check && grep -qF 'reading a modelled compartment value as a measured one' docs/MODEL.md
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

## Written 2026-09-13: the table, and the check that keeps its last column honest

`docs/MODEL.md` gains `## Reasonably foreseeable misuse, and the hazards the
presentation carries`, placed after the intended-use section `PL-BLHV` added and
before "Purpose" — ISO 14971's own order, intended use then hazard.

**Six rows, each naming the test that holds it.** Reading a correct
concentration as another agent's; a halted run as a paused one; a setting above
the vaporizer maximum as having been simulated; a displayed value as resolved to
its last digit; a control mark as a measurement; and a modelled compartment
value as a measured one. The first five cite ten tests between them, every name
verified to resolve before it was written down.

**The sixth row says "partially mitigated" and the section explains why rather
than implying otherwise.** Three statements exist and they cover different
surfaces: `README.md` has the global claim and a learner never opens it; the
control-input timeline has `"Settings only - not a measurement."`, exact and
covering the marks only; and the interface's standing notice is a *use*
disclaimer, which says what the tool is for rather than how to read a number.
Nothing tells a reader that the compartment readouts and chart traces are
modelled. The owner agreed the interface should carry an interpretation
statement; wording and placement are an interface change, so they are
`PL-2K1R`, filed with the existing timeline phrasing named as the pattern.

**`tools/doc_check.py check_named_tests` is what stops the last column rotting**,
and it is the reason the table can carry test names at all — a right-hand column
of prose nobody re-checks is decoration, and worse than none because it looks
authoritative. Every `` `test_...` `` named in `docs/MODEL.md` must resolve to a
definition under `tests/` or `subprojects/docket/tests/`.

**Scoped to `docs/MODEL.md`, on a count rather than a preference.** Measured
across every markdown file in the tree: 161 test names cited, 21 resolving to
nothing, and **all 21 in `docs/items/`** — correct there, because an item brief
names the test its work will add, the same forward reference a `verify:` command
makes. A tree-wide check would fail the queue for doing its job. A specification
asserts what holds now, so only it is held to this.

This is the cheap half of `PL-8LDF` (tie MODEL.md's required invariants to named
tests), which keeps the annotation pass over the eighteen invariants — the
eighteen judgments were always the work, and the resolver was always the part a
script could do. `PL-8LDF` is smaller for it and unblocked by it.

**One defect found in the check and fixed before it landed.** It first declined —
"not checked" — on any repository whose `docs/MODEL.md` names no test at all,
which broke three existing tests and was a real defect rather than test
friction: a decline claims a gap, and there is no gap until a name is cited.
Reading the citations *before* looking for the suite fixed it, and `CLAUDE.md`'s
rule that a check firing every run without changing a decision is a defect in
the check is what named it.

**`PL-8LDF` is confirmed as separate work, not merged into this.** Checked
against the eighteen invariants rather than assumed: exactly one of this table's
rows corresponds to an existing Required invariant (the vaporizer-maximum
rejection). The other five are presentation hazards the invariants do not reach,
because every invariant in that list is about core numerics and state. A merged
table would give its "test" column two meanings — implementation verification in
some rows, presentation validation in others — which is the distinction
`.claude/rules/expert-review.md` requires be kept.

**Verified.** The `verify:` command's `grep` fails against `origin/main`'s copy
of `docs/MODEL.md` and the whole command passes here. `make check` green. Docs
swept: `docs/MODEL.md` (edited), `README.md` (read — its "Every value on screen
is a model output, never a measurement" is the global form of the missing
interface line and is cited in `PL-2K1R` as the sentence to adapt; correct as it
stands), `docs/ARCHITECTURE.md` (read — no statement about hazards or the
displayed-value disclaimers, so nothing is owed).
