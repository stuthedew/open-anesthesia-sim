---
id: PL-4ZVH
title: pr_body_check reads a recovered record's fields and an appended trailer one physical line at a time, so a commit: value folded onto the next line reads as empty and anchors skips that record silently, and a folded Co-authored-by trailer is left in the body; latent
status: untriaged
feature: one-answer
touches: tools/pr_body_check.py, tests/unit
added: 2026-10-04
---

**Problem.** pr_body_check reads a recovered record's fields and an appended trailer one physical line at a time, so a commit: value folded onto the next line reads as empty and anchors skips that record silently, and a folded Co-authored-by trailer is left in the body; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

A recovered record follows the item front-matter convention, where an indented line continues a value (`model._fold`). `parse_record` reads `commit:` over an indented SHA as an empty commit, and `anchors` then returns 0 - the record never checked - though its own failure message asks for exactly such a hand edit. `APPENDED_TRAILER_RE`, in `normalise` for `--compare` only, does not strip a trailer `git interpret-trailers` folds onto a second line, so the verdict reads `differs`. Latent: none of the 265 records folds a value, and none of 1,037 trailers is folded.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
