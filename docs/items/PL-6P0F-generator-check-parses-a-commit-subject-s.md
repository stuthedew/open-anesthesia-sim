---
id: PL-6P0F
title: generator_check parses a commit subject's leading ids differently from vcs.leading_ids - case-sensitive, commas only, colon required - so creation_parents misses the capturing parent of 74 of 729 item-adding commits on origin/main and the self-generation ratio it surfaces candidates from undercounts
status: untriaged
feature: one-answer
touches: tools/generator_check.py, tests/unit/test_generator_check.py
added: 2026-09-25
impairs-generators: tools/generator_check.py's leading-id parse is case-sensitive, comma-only and colon-required where vcs.leading_ids is not, so creation_parents drops the capturing parent of 74 of 729 item-adding commits and the self-generation ratio undercounts
---

**Problem.** generator_check parses a commit subject's leading ids differently from vcs.leading_ids - case-sensitive, commas only, colon required - so creation_parents misses the capturing parent of 74 of 729 item-adding commits on origin/main and the self-generation ratio it surfaces candidates from undercounts

Reproduced by importing both: `PL-4JHS backfill ... (#809)` gives `[PL-4JHS]` to `vcs.leading_ids` (`vcs.py:666`) and `[]` to `tools/generator_check.py:113`; `pl-b8hz: x` likewise. Over origin/main, 74 of 729 commits that add an item differ.

**Why it matters.** `tools/generator_check.py` is the candidate-surfacing half of generator identification (`generator_paths`), so an undercounted parent is a cluster never surfaced - and nothing in the store says one went unfound.

**Done when.** generator_check imports the leading-id parse from docket (or `store.ID_PATTERN` plus the same separator grammar), and a test holds both reproductions.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
