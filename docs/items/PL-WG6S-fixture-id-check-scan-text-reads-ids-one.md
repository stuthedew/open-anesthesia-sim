---
id: PL-WG6S
title: fixture_id_check.scan_text reads ids one physical line at a time in a shell file under .claude/, where a backslash-newline joins a word, so an id split that way is reported as malformed and the joined one is missed; latent
status: untriaged
feature: one-answer
touches: tools/fixture_id_check.py, tests/unit
added: 2026-10-04
---

**Problem.** fixture_id_check.scan_text reads ids one physical line at a time in a shell file under .claude/, where a backslash-newline joins a word, so an id split that way is reported as malformed and the joined one is missed; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

POSIX XCU § 2.2.1. `collect` hands `scan_text` every file under `.claude/`, hook scripts included; over "echo PL-K7\" / "QX" / "echo PL-K7QX\" / "Z" it reports `PL-K7` on line 1, where bash reads `PL-K7QX`, which is valid, and `PL-K7QXZ`, which is not. Markdown and JSON under `.claude/` cannot join a token, so only shell files carry the form. Latent and contrived: no `PL-...\` ends a line anywhere under `.claude/`. The lowest-consequence member the sweep found.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
