---
id: PL-TN0G
title: Nothing flags a test assertion that never decides a result: mutation testing asks whether some assertion catches each fault, never whether each assertion catches a fault the others miss, so the step-size test's 0.5% limit sat beside a stricter 1e-14 limit from #376 (2026-09-05) until a prose rewrite found it (PL-VXM0). Add a warning that switches off each assertion of a changed simulator test in turn and names any whose removal loses no caught mutant, and run it once over the existing unit and reference tests
status: untriaged
feature: dead-test-limits
touches: tools/diff_mutation.py, tests/unit/test_diff_mutation.py, docs/mutation-testing.md
added: 2026-11-03
verify: grep -q 'never decides a result' docs/mutation-testing.md
---

**Problem.** Nothing flags a test assertion that never decides a result: mutation testing asks whether some assertion catches each fault, never whether each assertion catches a fault the others miss, so the step-size test's 0.5% limit sat beside a stricter 1e-14 limit from #376 (2026-09-05) until a prose rewrite found it (PL-VXM0). Add a warning that switches off each assertion of a changed simulator test in turn and names any whose removal loses no caught mutant, and run it once over the existing unit and reference tests
