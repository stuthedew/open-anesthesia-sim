---
id: PL-LBMQ
title: tests/unit/test_dashboard_frame.py: the bookmark panel section comment says reaching a mark (PL-CTD7) is not built, but later tests in the file check rows that say a mark was reached (found in the PL-FDMJ prose pass, 2026-10-25)
priority: P3
effort: S
status: done
classes: docs
feature: stale-source-claims
touches: tests/unit/test_dashboard_frame.py
added: 2026-10-25
closed: 2026-10-25
payoff: the bookmark panel's tests say what they test, including reaching a mark
verify: ! grep -qF 'Detection is `PL-CTD7` and is not' tests/unit/test_dashboard_frame.py
---

**Problem.** tests/unit/test_dashboard_frame.py: the bookmark panel section comment says reaching a mark (PL-CTD7) is not built, but later tests in the file check rows that say a mark was reached (found in the PL-FDMJ prose pass, 2026-10-25)

**Reproduced 2026-10-25.** `grep` on `main` at `b6ff4443` finds line 2848 of `tests/unit/test_dashboard_frame.py`: "Detection is `PL-CTD7` and is not" built, above tests that check rows saying a mark was reached.

**Why it matters.** A reader looking for where reaching a mark is tested is told the feature does not exist, in the file that tests it.

**Done when.** The section comment describes what the tests below it check, including the reached rows. No test changes behaviour.
