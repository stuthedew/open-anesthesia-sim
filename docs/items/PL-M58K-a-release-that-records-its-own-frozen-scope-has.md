---
id: PL-M58K
title: A release that records its own frozen scope has to call it a debt gate, which it is not
status: untriaged
touches: subprojects/docket/src/docket/roadmap.py, ROADMAP.md
added: 2026-08-30
---

**Problem.** A release that records its own frozen scope has to call it a debt gate, which it is not

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `GATE_SUBSECTION = "debt gate"` in
`subprojects/docket/src/docket/roadmap.py` is the only machine-readable hook by
which a milestone section declares a frozen list, and `wave()` follows the
nearest one. That is how v0.2.8 was scoped (PL-51T3): its seventeen entries are
recorded under `### Debt gate: the frozen list` so the beat follows them.

Eleven of those seventeen are not debt. `ROADMAP.md`'s own "What counts" says
so explicitly - new workflow capability is not debt and does not hold a gate -
so the section is now a paragraph of prose explaining that the heading above it
does not mean what the document defines it to mean.

**Why it matters.** `ROADMAP.md`'s definitions are load-bearing: the debt gate
rule is what stops a milestone starting on unpaid debt, and "What counts" is
what stops it being renegotiated. A heading that names something the document
defines as not being that thing weakens both, and it recurs - every future
release that wants to come ahead of an open gate has to overload the same
heading.

**Where.** `subprojects/docket/src/docket/roadmap.py` (`GATE_SUBSECTION`,
`parse_milestones`, `MilestoneSection.records_a_gate`, `gate_status`), the
v0.2.8 section of `ROADMAP.md`, and the v0.4.0 section that uses the heading
for a real gate.

**Approach.** Read a second heading - a frozen scope - alongside the debt gate,
both parsed the same way and both taking the beat, so a release says which kind
of list it is recording in the heading rather than in a paragraph beneath it.
The counting logic is identical; only the name and what the digest calls it
change. Keep `debt gate` working unchanged so v0.4.0's section is untouched.

**Not urgent.** The mechanism is correct today and the prose says what is true.
This is a naming defect in a document whose naming is the mechanism, not a
wrong answer from the tool.

**Done when.** A release can record a frozen scope under a heading that names
it accurately, `wave()` follows it exactly as it follows a debt gate, a test
names both kinds, and v0.2.8's section no longer needs a paragraph explaining
its own heading.
