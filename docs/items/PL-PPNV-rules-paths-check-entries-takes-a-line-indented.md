---
id: PL-PPNV
title: rules_paths_check.entries takes a - line indented past its sequence's dash for a new glob, where YAML continues the item's plain scalar, so the check passes while the harness reads one glob that matches nothing; latent
status: untriaged
feature: one-answer
touches: tools/rules_paths_check.py, tests/unit
added: 2026-10-04
---

**Problem.** rules_paths_check.entries takes a - line indented past its sequence's dash for a new glob, where YAML continues the item's plain scalar, so the check passes while the harness reads one glob that matches nothing; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

YAML 1.2.2 § 7.3.3: a line indented past the sequence's `- ` column continues the item's plain scalar, even when it opens with `- `. `entries` reads `paths:` over `  - /src/**` and `    - /tests/**` as two globs, where PyYAML 6.0.3 and ruamel read one, `/src/** - /tests/**`, and `problems` returns nothing on a tree holding both directories - the silent "Nowhere" the module exists to catch. The same continuation without its dash raises `Unreadable`, as the function's contract says this form should. Latent: all ten `.claude/rules` front matters write `paths:` at column 0 with one quoted glob per line.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
