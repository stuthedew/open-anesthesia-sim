---
id: PL-0779
title: docket new and docket set write a command-line value holding a newline verbatim and exit 0, leaving a file the next check refuses; latent
status: untriaged
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/model.py, subprojects/docket/tests
added: 2026-10-04
---

**Problem.** docket new and docket set write a command-line value holding a newline verbatim and exit 0, leaving a file the next check refuses; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

A title or field value passed with an embedded newline is written as it stands at exit 0, and the next `bin/docket check` flags the file, so the refusal arrives after the write rather than instead of it. Not a member of `PL-R417`: the writer's validation, not a reader. Latent: no capture has passed one.
