---
id: PL-CMJ5
title: A test's expected value taken from the code or data under test rather than an independent source: four members, ended by the test-oracles rule on 2026-10-17
priority: P3
effort: S
status: done
classes: defect
feature: defect-review-2026-10
milestone: v0.6.4
touches: docs/items
added: 2026-10-25
closed: 2026-10-25
pr: 1783
payoff: the audit records that dependent test oracles were one mechanism behind four defects, and which rule ended it
verify: grep -qE '^generator: spent' docs/items/PL-CMJ5-*.md
root-cause-of: PL-H8QP, PL-H1JH, PL-JPS2, PL-QJXS
generator: spent - .claude/rules/test-oracles.md, added 2026-10-17 by #1497, requires a simulator test's expected value from an independent source and loads with every test file
misread: Where a test's expected value comes from: a source independent of the code under test
---

**Problem.** A test's expected value taken from the code or data under test rather than an independent source: four members, ended by the test-oracles rule on 2026-10-17

**The fact the members misread.** A test can catch a wrong value only if its expected value comes from somewhere the code under test does not:

- `PL-H8QP`: the reads-the-file tests used inputs equal to the core defaults, so they could not tell a file read from a default.
- `PL-H1JH`: MAC-awake fractions and standard deviations had no pin from the adopted primary source.
- `PL-JPS2`: both MAC-awake band tests took their expected band from the snapshot under test.
- `PL-QJXS`: no test compared an agent-switched run with a fresh run of the new agent.

**Why it is spent.** `.claude/rules/test-oracles.md`, added on 2026-10-17 by `#1497` (`PL-3KMD`, `PL-6JKB`), requires a simulator test's expected value to come from an independent source, and it loads whenever a session opens a test. No member has been filed since.

**Why it matters.** The audit of where product defects come from needs each shared cause recorded, with the rule that ended it.

**Done when.** This head records its members and why it is spent.

**Generator check.** Recorded for the audit by `PL-R4Y2`'s defect review.
