---
id: PL-FTDB
title: bin/docket set writes a verify: command that already passes, because it validates without running the verify it is writing, so a grep that matches its own frontmatter line (PL-CBDX, 2026-09-25) is accepted and fails the next make check
status: untriaged
feature: set-parity
touches: subprojects/docket/src/docket/cli.py
added: 2026-09-25
---

**Problem.** bin/docket set writes a verify: command that already passes, because it validates without running the verify it is writing, so a grep that matches its own frontmatter line (PL-CBDX, 2026-09-25) is accepted and fails the next make check
