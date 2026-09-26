---
id: PL-6P0F
title: generator_check parses a commit subject's leading ids differently from vcs.leading_ids - case-sensitive, commas only, colon required - so creation_parents misses the capturing parent of 74 of 729 item-adding commits on origin/main and the self-generation ratio it surfaces candidates from undercounts
priority: P2
effort: S
status: done
classes: defect
feature: one-answer
milestone: v0.5.12
touches: tools/generator_check.py, tests/unit/test_generator_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-25 with the one-answer batch
added: 2026-09-25
closed: 2026-09-26
pr: 1069
payoff: generator_check credits every capture to the item whose work filed it, so a self-generating cluster is no longer hidden behind a subject with no colon or a lower-case id
verify: grep -q 'def test_creation_parents_reads_leading_ids_as_docket_does' tests/unit/test_generator_check.py
impairs-generators: tools/generator_check.py's leading-id parse is case-sensitive, comma-only and colon-required where vcs.leading_ids is not, so creation_parents drops the capturing parent of 74 of 729 item-adding commits and the self-generation ratio undercounts
---

**Problem.** generator_check parses a commit subject's leading ids differently from vcs.leading_ids - case-sensitive, commas only, colon required - so creation_parents misses the capturing parent of 74 of 729 item-adding commits on origin/main and the self-generation ratio it surfaces candidates from undercounts

Reproduced by importing both: `PL-4JHS backfill ... (#809)` gives `[PL-4JHS]` to `vcs.leading_ids` and `[]` to `tools/generator_check.py`'s `LEADING_IDS_RE`, as `creation_parents` applies it; `pl-b8hz: x` likewise. Over origin/main, 74 of 729 commits that add an item differ.

**Re-confirmed 2026-09-25 against 46954a81**, importing both: the same two subjects give `['PL-4JHS']` and `['PL-B8HZ']` to `vcs.leading_ids` and `[]` to `creation_parents`' parse, and 74 of the now 738 item-adding commits on `origin/main` differ. Today's merges touched neither parser.

**Generator check.** It is an instance of PL-PVW2's fact, which spelling of a repeated predicate is the answer. The predicate is which ids a subject leads with: `tools/generator_check.py` borrows `store.ID_PATTERN` (PL-KYW3) but spells the separator grammar again. It is not a one-off, because it is the second time this file restated a docket grammar, and PL-KYW3 was the first. **`impairs-generators:` stands.** `touches` reaches `generator_paths`, the field names the broken function, and the undercount prints as measured, so a self-generating cluster can go unsurfaced with nothing saying so. That ranks it on the generator tier, and under `CLAUDE.md` the same session fixes it or ends its reply with a fresh-session prompt.

**Why it matters.** `tools/generator_check.py` is the candidate-surfacing half of generator identification (`generator_paths`), so an undercounted parent is a cluster never surfaced - and nothing in the store says one went unfound.

**Done when.** generator_check imports the leading-id parse from docket (or `store.ID_PATTERN` plus the same separator grammar), and a test holds both reproductions.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
