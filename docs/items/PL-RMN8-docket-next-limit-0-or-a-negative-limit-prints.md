---
id: PL-RMN8
title: docket next --limit 0 (or a negative limit) prints 'Nothing is ready to start' while work is startable, because the limit slices the ranking to nothing rather than being refused
status: untriaged
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-22
---

**Problem.** docket next --limit 0 (or a negative limit) prints 'Nothing is ready to start' while work is startable, because the limit slices the ranking to nothing rather than being refused
