---
id: PL-M58K
title: A release that records its own frozen scope has to call it a debt gate, which it is not
priority: P3
effort: S
status: dropped
classes: docs, infra
feature: planning-cadence
touches: subprojects/docket/src/docket/roadmap.py, ROADMAP.md
added: 2026-08-30
closed: 2026-09-12
reason: one historical section, already annotated: of the three 'Debt gate: the frozen list' headings only v0.2.8's is a frozen scope rather than a debt gate, that release is complete, and its section already explains that its heading is the hook bin/docket wave reads
verify: uv run pytest subprojects/docket/tests/test_roadmap.py -q && grep -rq 'def test_a_frozen_scope_heading_is_followed_like_a_debt_gate' subprojects/docket/tests
---

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

**Dropped 2026-09-12**, by the workflow-lane consolidation pass (`PL-6ZQY`).
The premise was checked against the tree by an adversarial reviewer whose
default was to refuse, and it did not survive:

> One historical section, already annotated, and the recurrence path is now closed. `### Debt gate: the frozen list` appears three times in ROADMAP.md (lines 483, 913, 1404); only v0.2.8's is a frozen scope rather than a debt gate, that release is completed, and its section already carries the paragraph explaining that its own heading is the hook `bin/docket wave` reads rather than a claim of debt. The two later uses (v0.4.0, v0.5.0) both scope themselves to items that are debt by "The debt gate", so the overload has cost nothing a second time. It also cannot easily cost a third: the timeline records that the v0.4.x track "freezes no gate and takes no section of its own" (project owner, 2026-09-05), that rows 1 and 2 are the only releases whose whole content is a frozen list, and v0.5.1 — a patch that does take a section — records no gate. The defect itself is unfixed: GATE_SUBSECTION = "d

What the file keeps that exists nowhere else, which is why it is dropped rather
than deleted: Two things, both cheap. First, the item's design sketch — read a second "frozen scope" heading alongside "debt gate", both parsed identically and both taking the beat — exists nowhere else; it survives only because a dropped item keeps its file. Second, the item's figure "eleven of those seventeen are not debt" is lost, but it is already stale: the v0.2.8 list has grown to 38 entries in two groups (22 and 16), and the debt/non-debt split is now recorded in those group headings instead. Nothing d

