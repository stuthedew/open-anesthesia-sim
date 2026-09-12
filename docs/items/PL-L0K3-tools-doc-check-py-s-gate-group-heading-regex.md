---
id: PL-L0K3
title: tools/doc_check.py's gate-group heading regex requires the literal word 'entries', so a one-item post-freeze addition to a frozen list can be written only as ungrammatical '1 entries' or as an uncounted heading whose entry is then attributed to the group above it
priority: P2
effort: S
status: done
classes: defect, infra
feature: doc-consistency-checks
milestone: v0.4.13
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-10
closed: 2026-09-10
pr: 494
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_a_gate_group_holding_exactly_one_entry_may_say_so_in_the_singular' tests/unit/test_doc_check.py
---

**Problem.** tools/doc_check.py's gate-group heading regex requires the literal word 'entries', so a one-item post-freeze addition to a frozen list can be written only as ungrammatical '1 entries' or as an uncounted heading whose entry is then attributed to the group above it

**Why it matters.** `ROADMAP.md`'s frozen debt-gate lists are the record of
what a milestone waits on, and a post-freeze addition is written as a dated
group with its own count. `GATE_GROUP_RE` recognizes such a heading only by the
pattern `<number> entries`, so a group holding exactly one item had no correct
form. Both available spellings were wrong in a different way, and the second is
the dangerous one:

- `— 1 entries` passes the check and puts bad grammar into the document a
  reader consults to learn what the release is blocked on.
- Omitting the count leaves a line the regex does not match at all. The parser
  documents that case as deliberate — "a heading stating no readable count is
  not one of these and is passed over" — so the entry beneath it is counted
  into the *previous* group, and the check reports that the group above
  miscounted itself. The heading reads correctly to a person and the arithmetic
  is silently attached to the wrong date and the wrong rule.

Met 2026-09-10 while placing `PL-LT51` on v0.5.0's gate under the unconditional
safety/science exception — a single item, filed the same day, and the first
one-item post-freeze addition this project has had.

**The fix.** `entr(?:y|ies)` in `GATE_GROUP_RE` only, plus `item ids?` in the
same expression for the same reason. **`ENTRY_COUNT_RE` is deliberately left
plural-only.** It scans ordinary prose and table cells rather than headings, so
admitting the singular there would read "the one entry in it a user cannot set"
— a real bullet in this repository's own gate list, from `PL-0Q1T` — as a claim
that a list holds one thing. The narrow change is the whole change.

**Proven both ways, 2026-09-10.** Two tests were added to
`tests/unit/test_doc_check.py`: one asserting a singular heading is accepted
and its list totals correctly, one asserting the count under it is still
enforced. Against the pre-fix regex both fail; against the fix both pass.

**Outcome.** Landed with `PL-LT51`'s gate placement, which is what needed it.
