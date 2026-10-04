---
id: PL-PXT7
title: contrast_check reads a colour only from a constant that is exactly #RRGGBB, treats only the :disabled literal as a disabled state, and lists files without -z, so a colour built from parts, a Qt :!enabled rule and a non-ASCII path go unread; latent
status: untriaged
touches: tools/contrast_check.py, tests/unit
added: 2026-10-04
---

**Problem.** contrast_check reads a colour only from a constant that is exactly #RRGGBB, treats only the :disabled literal as a disabled state, and lists files without -z, so a colour built from parts, a Qt :!enabled rule and a non-ASCII path go unread; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`HEX_COLOR_RE` (`^#[0-9A-Fa-f]{6}$`) reads a colour only from a string constant that is exactly `#RRGGBB`; the disabled-state reader knows `:disabled` and not Qt's `:!enabled`; and its `git ls-tree` runs without `-z`, so git C-quotes a non-ASCII path. Not members of `PL-R417`. Latent: the stylesheets use whole constants and `:disabled`, and no tracked path is non-ASCII.
