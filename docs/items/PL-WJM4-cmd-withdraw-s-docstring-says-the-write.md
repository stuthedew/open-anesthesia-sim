---
id: PL-WJM4
title: cmd_withdraw's docstring says the write replaces one line, but with_front_matter_value replaces the key's line and every continuation _fold gives it; latent
status: untriaged
touches: subprojects/docket/src/docket/cli.py
added: 2026-10-04
---

**Problem.** cmd_withdraw's docstring says the write replaces one line, but with_front_matter_value replaces the key's line and every continuation _fold gives it; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`cli.py`:1663-1666 describes the `recurrences:` withdrawal as a one-line replace; the write goes through `with_front_matter_value`, which replaces the key line and its folded continuations. A docstring that no longer says what the code does.
