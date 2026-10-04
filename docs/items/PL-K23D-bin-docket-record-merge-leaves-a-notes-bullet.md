---
id: PL-K23D
title: bin/docket record --merge leaves a notes bullet that notes_bullets declines unrestated without saying so, so the command's report omits the bullet it could not write; latent
status: untriaged
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/release.py, subprojects/docket/tests
added: 2026-10-04
---

**Problem.** bin/docket record --merge leaves a notes bullet that notes_bullets declines unrestated without saying so, so the command's report omits the bullet it could not write; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`cli._restate_notes` goes through `release.restate_references`, which drops `notes_bullets`' decline record, so a bullet continued from the margin is left alone and `record --merge` does not name it; `bin/docket check` does. Its output is true about what it wrote, which is why it is not a member of `PL-R417`, but it is a decline that stops short of the answer that ran. Latent: none of the 79 notes files holds the form.
