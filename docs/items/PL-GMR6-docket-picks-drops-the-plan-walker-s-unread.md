---
id: PL-GMR6
title: docket picks drops the plan walker's unread entries, so a gate entry the walker declines by name is left out of the pick list at exit 0, where docket wave names it and exits 1; latent
status: untriaged
feature: one-answer
touches: subprojects/docket/src/docket/picks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests
added: 2026-10-04
---

**Problem.** docket picks drops the plan walker's unread entries, so a gate entry the walker declines by name is left out of the pick list at exit 0, where docket wave names it and exits 1; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`Wave.unread` carries the list walker's decline (`PL-MFVV`, `#1343`); `picks` (`#1345`, after it) builds a `Picks` with no field for it, and `cmd_picks` exits 0. With a gate entry whose bold lead wraps onto a lazy line, `plan.unread` names the line and the pick list simply lacks the entry. The decline reached `check`, `wave` and the digest and stopped there. Latent: `wave(ROADMAP.md).unread` is empty, and `doc_check` fails each such line in `make check`.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
