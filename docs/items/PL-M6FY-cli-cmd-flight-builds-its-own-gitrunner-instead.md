---
id: PL-M6FY
title: cli.cmd_flight builds its own GitRunner instead of the invocation's, so flight loses the cat-file memo every other command shares
status: untriaged
added: 2026-09-21
---

**Problem.** cli.cmd_flight builds its own GitRunner instead of the invocation's, so flight loses the cat-file memo every other command shares
