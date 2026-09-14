---
id: PL-0QLX
title: tests/unit/test_docket_branch_guard.py and test_docket_digest_hook.py pin PATH to /usr/bin:/bin:/usr/local/bin, so on a Mac whose /usr/bin/python3 is Apple's 3.9 bin/docket fails on datetime.UTC, both hooks exit 0 silently, and eight tests fail locally while CI is green
status: untriaged
added: 2026-09-14
---

**Problem.** tests/unit/test_docket_branch_guard.py and test_docket_digest_hook.py pin PATH to /usr/bin:/bin:/usr/local/bin, so on a Mac whose /usr/bin/python3 is Apple's 3.9 bin/docket fails on datetime.UTC, both hooks exit 0 silently, and eight tests fail locally while CI is green
