---
id: PL-RCL9
title: docket trend --no-git builds its lines-written series from an empty Churn() that declines nothing, so a trend under the flag reads as a repository nobody committed to rather than saying the history went unread
status: untriaged
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-23
---

**Problem.** docket trend --no-git builds its lines-written series from an empty Churn() that declines nothing, so a trend under the flag reads as a repository nobody committed to rather than saying the history went unread
