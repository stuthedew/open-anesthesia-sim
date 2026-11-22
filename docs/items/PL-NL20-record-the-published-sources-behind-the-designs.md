---
id: PL-NL20
title: Record the published sources behind the designs of PL-P5W1 (copy check reads the stored state instead of writing it back) and PL-S8FM (control change refused after an unrecorded setting)
status: done
feature: replay-findings
touches: docs/items/PL-P5W1-a-copy-of-a-run-opened-from-a-system-whose.md, docs/items/PL-S8FM-a-circuit-or-alveolar-volume-written-directly.md
added: 2026-11-22
closed: 2026-11-22
pr: 2261
---

**Problem.** Record the published sources behind the designs of PL-P5W1 (copy check reads the stored state instead of writing it back) and PL-S8FM (control change refused after an unrecorded setting)

**Why.** The owner asked on 2026-11-22 whether everything being built
follows researched best practice. The designs of `PL-P5W1` and `PL-S8FM`
merged in #2245 were reported to him without sources. `PL-S8FM` already
cited one paper, and `PL-P5W1` cited none.

**Recorded 2026-11-22.** The sources were read that day and recorded in each
item: Goldberg 1991 (Theorem 7) and the Python `pickle` documentation for
`PL-P5W1`, and Meyer, Arkadova and Kogtenkov (arXiv:2109.06557v12, § 8.3,
now quoted at the subsection that applies) and the project's safety-critical
standard for `PL-S8FM`. Both support the designs as built, so no code
changes.

**Generator check.** The cause is a design reported before its sources
were recorded. `.claude/rules/instruction-writing.md` rule 10 now requires
the research before a question reaches the owner (`PL-W7HW`). These two
designs were not questions, so that rule did not reach them. The coordinator
relay that started them already said that non-clinical design calls are
decided by researched best practice. This session applied it to one item and
not the other, which is a lapse rather than a missing rule. No new item.

**Docs checked.** The two item files only. No simulator document states
either design's rationale.
