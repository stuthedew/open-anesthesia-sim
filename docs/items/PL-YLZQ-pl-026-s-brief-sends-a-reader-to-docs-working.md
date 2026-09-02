---
id: PL-YLZQ
title: PL-026's brief sends a reader to docs/WORKING_NOTES.md for its own rejected options and reasoning, which the rewritten split calls backwards
priority: P2
effort: S
status: done
classes: docs
feature: dev-tooling
milestone: v0.2.11
touches: docs/items/PL-026-make-the-simulation-step-transactional-so-a.md, docs/WORKING_NOTES.md
added: 2026-09-01
closed: 2026-09-02
pr: 204
verify: python3 tools/doc_check.py check && ! grep -q 'Decided, not yet implemented' docs/WORKING_NOTES.md && grep -q 'circuit_concentration_fraction' docs/items/PL-026-make-the-simulation-step-transactional-so-a.md
---

**Problem.** `docs/items/PL-026-make-the-simulation-step-transactional-so-a.md:30`
ends its **Decision (2026-08-24).** paragraph with "Rejected options, the state
inventory, and the reasoning are in `docs/WORKING_NOTES.md` under 'Decided, not
yet implemented'". `docs/WORKING_NOTES.md`'s "Decided, not yet implemented"
section is about `PL-026` and nothing else: the eight-float state table, the two
rejected display treatments and why the partial numbers have no teaching value,
and the argument for putting capture on each compartment rather than in
`AgentUptakeSystem`.

That is one item's own reasoning held in a second file. The rewritten split in
`docs/WORKING_NOTES.md`'s header and in `CLAUDE.md`'s capture bullet (both
2026-09-01) name this shape explicitly as the split applied backwards, and this
is the only instance of it in the tree — the other item briefs citing that file
either declare it in `touches`, record a doc sweep, or point the correct way
(`PL-6GS0` says its measured comparison "is carried in the item rather than
here").

**Why it matters.** The reasoning is what a session starting `PL-026` needs and
it is not where that session will look. `PL-026` is `P1`, `status: ready`,
`classes: safety, ux`, so the reader it strands is one about to change how a
failed simulation step leaves displayed state. The duplication is also live: the
item already restates the decision, the eight-float rationale and the first step
in its own words, so the two documents state one thread twice and both have to
stay true.

**Where.** Move `docs/WORKING_NOTES.md`'s "Decided, not yet implemented -
PL-026" section (40 lines) into the item, and delete the section rather than
leaving a stub — the file's header asks for exactly that when a thread stops
being one it is for. Check the state table survives the move: it is a Markdown
table of the eight dynamic fields, and it is the part of the reasoning the
implementation is checked against.

**Watch for.** Nothing else should be dragged along. The neighbouring threads
are cross-item or outlive their items and stay put; this section is the one that
is about a single open item.

**Done when.** `PL-026` carries its own rejected options, state inventory and
reasoning, `docs/WORKING_NOTES.md` has no "Decided, not yet implemented"
section, and no `grep -n 'WORKING_NOTES' docs/items/*.md` hit sends a reader
out of an item for that item's own reasoning.

**Outcome (2026-09-02).** Closed with `PL-026` (make the simulation step
transactional), on the same branch and in the same commit, under the rule that
a finding an in-progress item needs in order to be properly finished is worked
with it rather than after it. Implementing `PL-026` made
`docs/WORKING_NOTES.md`'s "Decided, not yet implemented" heading false the
moment it landed, so deleting the section was `PL-026`'s own close-out; the
reasoning it held — the eight-float state table, the two rejected display
treatments, and the argument for putting capture on each compartment — is now
in `PL-026`'s body, alongside an outcome section recording what was actually
built and where it departed from the table.
