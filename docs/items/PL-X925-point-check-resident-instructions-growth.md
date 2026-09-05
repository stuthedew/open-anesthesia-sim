---
id: PL-X925
title: Point check_resident_instructions' growth advisory at docs/resident-instructions.md, once PL-QV1F's character metric has landed
status: untriaged
added: 2026-09-05
---

**Problem.** Point check_resident_instructions' growth advisory at docs/resident-instructions.md, once PL-QV1F's character metric has landed

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `PL-JK0M` wrote `docs/resident-instructions.md`, the ledger of what
loads at launch and why - which block was routed where, which stayed, and which
reductions were considered and refused. Nothing points a session at it at the
moment the question arises.

`check_resident_instructions`'s growth advisory is that moment, and it already
asks the right question ("Two answers, and there is no third: route it ... or
keep it and say why"). What it cannot say today is that the answer for most of
the resident set has already been written down, so a session meeting the
advisory re-derives it.

**Why it was not done in `PL-JK0M`.** `PL-QV1F` is rewriting the same function
on `claude/resident-instruction-metric-0m5vrg` (#348) to measure characters
rather than lines - a 123-line diff over `tools/doc_check.py`. A one-sentence
edit to the advisory string would have conflicted with it for no gain, so the
sentence waits for that merge rather than racing it.

**Where.** `tools/doc_check.py`, `check_resident_instructions`; the advisory
strings only.

**Approach.** Add one clause naming `docs/resident-instructions.md` to the
growth advisory, and one to the grew-and-shrank advisory - the second is where
it matters most, because that advisory's whole question is whether removed
lines were routed somewhere or cut to make room, and the ledger is where the
routing is recorded. Check `tests/unit/test_doc_check.py`, which asserts on the
advisory text.

**Done when.** Both advisories name the ledger, and the doc_check tests pass.
