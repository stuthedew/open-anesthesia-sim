---
id: PL-LRBV
title: item_read_log writes a Grep pattern into a tab-separated record stripping only tabs and newlines, so a pattern holding a carriage return splits the record and item_reads.parse_log keeps the target cut short; latent
status: untriaged
touches: .claude/hooks/item_read_log.py, tools/item_reads.py, tests/unit
added: 2026-10-04
---

**Problem.** item_read_log writes a Grep pattern into a tab-separated record stripping only tabs and newlines, so a pattern holding a carriage return splits the record and item_reads.parse_log keeps the target cut short; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`item_read_log.py`:132 strips `\t` and `\n` from what it writes, and `item_reads.parse_log` (91) splits records with `splitlines()`, which also breaks at `\r`: a target `PL-K7QX\rPL-B1D0` comes back as `PL-K7QX`. Not a member of `PL-R417`. Latent.
