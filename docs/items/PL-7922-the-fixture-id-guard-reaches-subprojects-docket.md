---
id: PL-7922
title: The fixture-id guard reaches subprojects/docket/tests only, so the apparatus fixtures under tests/unit are held to no id grammar at all
status: untriaged
feature: one-id-grammar
touches: tools/generator_check.py, tools/doc_check.py, tools/item_reads.py
added: 2026-09-21
---

**Problem.** The fixture-id guard reaches subprojects/docket/tests only, so the apparatus fixtures under tests/unit are held to no id grammar at all

**Two instances, measured 2026-09-21 while doing `PL-DPY6`.**

- `tests/unit/test_generator_check.py` carried `PL-AAAA` as a fixture id in 20
  places - the file asserting the advisory's behaviour reproducing the defect it
  asserts about. `PL-DPY6` renamed them to `PL-8888`, so the instance is gone
  and the gap that let it stand is not.
- The gap is wider than `tests/unit`. Nothing scans `tools/` or `.claude/`
  either, which is how `tools/generator_check.py` printed `PL-AAAA` as the
  example to copy (`PL-DPY6`) and how `PL-A1B2` still stands in two `.claude/`
  files (`PL-3BZS`).

**Worth deciding when this is worked:** whether the guard moves out of
`subprojects/docket/tests/test_store.py` into a `tools/` check wired into
`make check`, which is the only tier that reaches `.claude/` and `tools/` as
well as both test trees. The AST walk it uses reads Python only, so a markdown
scanner is a second mechanism rather than a wider glob - and `citation-drift.md`
and `modes/ideas.md` are markdown. The recommendation is the `tools/` check over
a wider glob: same code, three more trees, one tier.
