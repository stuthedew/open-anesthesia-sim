---
id: PL-HDRN
title: bin/docket arm does not hold a simulator pull request whose blind generalist review passes were never run: PL-TDV9's close-out step 9 is prose only, and PL-W04Z measured that 5 of 6 simulator branches skipped close-out step 8's prose review until arm held for its Prose-review trailer; record the passes as a Blind-review trailer and hold on tools/blind_review.py --count
status: untriaged
feature: review-panel
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_arming.py, tools/blind_review.py, .claude/skills/docket/modes/close-out.md
added: 2026-10-24
---

**Problem.** bin/docket arm does not hold a simulator pull request whose blind generalist review passes were never run: PL-TDV9's close-out step 9 is prose only, and PL-W04Z measured that 5 of 6 simulator branches skipped close-out step 8's prose review until arm held for its Prose-review trailer; record the passes as a Blind-review trailer and hold on tools/blind_review.py --count
