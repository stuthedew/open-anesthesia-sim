---
id: PL-SJ1D
title: tests/unit/test_bookmarks.py: test_a_mark_inside_a_step_is_reached_at_the_step_s_end_and_not_rounded_back calls its 0.05 s step coarser than 0.1 s and says the reaching step ends at 45.4 s, but 0.05 s is finer and its reaching step ends at 45.35 s (found in the PL-FDMJ prose pass, 2026-10-25)
status: untriaged
feature: stale-source-claims
added: 2026-10-25
---

**Problem.** tests/unit/test_bookmarks.py: test_a_mark_inside_a_step_is_reached_at_the_step_s_end_and_not_rounded_back calls its 0.05 s step coarser than 0.1 s and says the reaching step ends at 45.4 s, but 0.05 s is finer and its reaching step ends at 45.35 s (found in the PL-FDMJ prose pass, 2026-10-25)
