---
id: PL-03GZ
title: doc_check candidates matches bare identifier tokens, so a diff touching settings.json or a test with a helper named _run emits 200 lines naming nothing relevant
status: dropped
added: 2026-09-04
closed: 2026-09-05
reason: Duplicate of PL-B2NS (doc_check candidates matches ordinary prose): same subcommand, same term-extraction decision, same fix. Its observation - a diff touching settings.json, or a test helper named _run, emitting 200 lines that name nothing relevant - is folded into PL-B2NS.
---

**Problem.** doc_check candidates matches bare identifier tokens, so a diff touching settings.json or a test with a helper named _run emits 200 lines naming nothing relevant

**Why it matters.**

**Where.**

**Done when.**
