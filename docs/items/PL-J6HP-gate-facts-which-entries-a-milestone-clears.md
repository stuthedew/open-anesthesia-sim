---
id: PL-J6HP
title: Gate facts - which entries a milestone clears itself, which are deferred, which closed entries carry the release that took them, how many a heading holds - live in ROADMAP.md prose that plan.py, roadmap.py and tools/doc_check.py each read on their own, so every new phrasing or fact arrives as a new item
priority: P2
effort: M
status: needs-decision
classes: defect, infra
feature: gate-list-integrity
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/plan.py, tools/doc_check.py, ROADMAP.md
added: 2026-09-23
payoff: each gate fact is read once, so a new way of writing one changes a parser instead of arriving in the queue as an item
root-cause-of: PL-H6VQ, PL-Z891, PL-YVP7, PL-B60Q, PL-JN3F, PL-RFHH
generator: live - gate membership, deferrals, marks and counts live in ROADMAP.md prose read by several functions; seven instances after PL-HWW1 closed, v0.6.0 gained 14 deferrals in 1.5 days (PL-KVDK), and PL-RFHH's rewording left every reader in place
---

**Problem.** `ROADMAP.md` records a debt gate's facts as prose, and each reader
re-derives them with a grammar of its own. `plan.gate()` decides what a
milestone clears itself by `feature`; `roadmap.gate_status` decides it by
`Required scope`, which is the rule the roadmap states; `tools/doc_check.py`
reads the deferral subsections with its own heading pattern and id extraction.
Counts and marks - how many entries a heading holds, the release a closed
deferral carries - sit in prose that no reader checks at all.

**Why it matters.** `PL-KVDK`'s first pass recorded this generator live on
`PL-RFHH`, the open item closest to the fix at the time. It moved here on
2026-09-23, when `PL-RFHH` closed on rewording `bin/docket gate` and `bin/docket
wave` so that neither prints the other's answer under its name. That removes
the collision and leaves this mechanism running, and closing a head on a
partial fix is how `PL-HWW1`, the earlier head for gate prose, went on to seven
more instances. Members: `PL-H6VQ` and `PL-Z891` (`doc_check`'s deferral
reading), `PL-YVP7` and `PL-RFHH` (two readings of what a milestone clears
itself), `PL-JN3F` (a heading count nothing reads) and `PL-B60Q` (a marking rule
stated inside one milestone's subsection).

**Generator check.** The head of one - see above.

**Decision needed.** Which route stops the mechanism. One is a single reader:
every gate fact parsed once in `docket.roadmap`, with `tools/doc_check.py` and
`plan.gate()` taking that parse instead of re-deriving it. The other moves the
facts out of prose into records no reader can mis-parse. Count the readers and
the facts each route has to carry before choosing. The first changes no stored
format, so it is the one to cost first.

**Done when.** Each gate fact the roadmap records has one reader, so a new
phrasing of one changes that reader instead of arriving as an item.
