---
id: PL-MR8Z
title: docket verify's unified-diff reader cannot read git's quoted header path and takes a removed -- or added ++ content line for a file header, so a deleted assertion in a file whose name git quotes, or a content line opening with two signs, drops out of the line reading; latent
status: untriaged
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests
added: 2026-10-04
---

**Problem.** docket verify's unified-diff reader cannot read git's quoted header path and takes a removed -- or added ++ content line for a file header, so a deleted assertion in a file whose name git quotes, or a content line opening with two signs, drops out of the line reading; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`DIFF_HEADER_RE` (1622) cannot read a header path git quotes, so `_net_line_changes` assigns that file's lines to no file: a deleted `assert x == 1` in an unparseable `café.py` gives "PASS ... none" where `plain.py` gives "FAIL ... 1 line(s)". `_net_line_changes` tells a `---`/`+++` header from content by its second character, so a removed line whose content opens `--` and an added one opening `++` are dropped: a diff holding `--1` and `++2` loses both. Both reach only the line reading: a file the interpreter cannot parse, and the `.toml`, `.cfg` and `.ini` files the suppression check reads by line. Not a member of `PL-R417`. Latent: git quotes no tracked path.
