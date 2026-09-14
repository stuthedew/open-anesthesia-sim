---
id: PL-0QLX
title: tests/unit/test_docket_branch_guard.py and test_docket_digest_hook.py pin PATH to /usr/bin:/bin:/usr/local/bin, so on a Mac whose /usr/bin/python3 is Apple's 3.9 bin/docket fails on datetime.UTC, both hooks exit 0 silently, and eight tests fail locally while CI is green
status: dropped
added: 2026-09-14
closed: 2026-09-14
reason: duplicate of PL-Y6W9, captured eight minutes apart on another branch for the same eight red tests; PL-Y6W9 carries the fuller brief, was the one the project owner named, and closed in #584 with the fix
---

**Problem.** tests/unit/test_docket_branch_guard.py and test_docket_digest_hook.py pin PATH to /usr/bin:/bin:/usr/local/bin, so on a Mac whose /usr/bin/python3 is Apple's 3.9 bin/docket fails on datetime.UTC, both hooks exit 0 silently, and eight tests fail locally while CI is green

**Why it matters.** Nothing on its own: the finding is real and `PL-Y6W9` (the
same eight hook tests red under macOS's system `python3`) carries it. The two
were captured eight minutes apart, this one on `claude/pensive-haslett-0f5025`
and `PL-Y6W9` on `claude/trusting-cerf-468dc8`, each by a session running
`make check` on the project owner's Mac. `PL-Y6W9` is the one kept: it holds
the brief, the reproduction and the fix, which landed in #584 and passes on the
owner's Mac (13 passed, 2026-09-14). `PL-8KPD` recorded this drop while the two
copies were still on separate branches.
