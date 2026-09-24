---
id: PL-1WV7
title: Once PL-N162 and PL-331V have both landed, route cli._cuts and cmd_release's release-train read through PL-N162's _holdings(args), so the digest walks the refs once rather than twice
status: untriaged
feature: claim-record
touches: subprojects/docket/src/docket/cli.py
added: 2026-09-24
---

**Problem.** Once PL-N162 and PL-331V have both landed, route cli._cuts and cmd_release's release-train read through PL-N162's _holdings(args), so the digest walks the refs once rather than twice
