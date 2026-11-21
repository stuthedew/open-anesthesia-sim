---
id: PL-FN11
title: An item that changes code records, when it closes, the pytest node ids of the tests that show its work, and docket checks once that each test is defined and that the closing branch added or changed it, in place of a verify: command
status: untriaged
feature: standing-weight
added: 2026-11-21
---

**Problem.** An item that changes code records, when it closes, the pytest node ids of the tests that show its work, and docket checks once that each test is defined and that the closing branch added or changed it, in place of a verify: command

**Why it matters.** The project owner chose this form on 2026-11-21 (`PL-LFJZ`, the count of what a test-named done-condition would have prevented). Of the 35 items under the root causes about `verify:` commands, it would have prevented 11 when the test is named at close, against 9 when it is guessed at triage: `PL-0M32` and `PL-6TN8` were both a test name guessed before the work. Checking once at close matters too: of 1,060 closed items whose condition named a test, 109 now name one that was later renamed or removed. At triage the item still says in words, under **Done when.**, what will be true. Code that only deletes something is `PL-N046`'s, since a deletion has no new test to name.
