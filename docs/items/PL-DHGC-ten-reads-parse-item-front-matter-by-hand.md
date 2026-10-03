---
id: PL-DHGC
title: Ten reads parse item front matter by hand instead of through docket.model, and one is wrong today: item_reads looks for status: done in a file's first 400 characters, so it reads 20 of 1,624 closed items as open; the others are generator_check's own parser, open-status set, list splits and a closure count that misses dropped, item_reads's --- split, and model's own parser restating FIELD_ORDER and LIST_FIELDS
priority: P2
effort: M
status: done
classes: defect
feature: read-facts-through-docket
milestone: v0.5.21
touches: tools/item_reads.py, tools/generator_check.py, subprojects/docket/src/docket/model.py, tests/unit/test_item_read_log.py, tests/unit/test_generator_check.py, subprojects/docket/tests/test_model.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
closed: 2026-10-01
pr: 1277
payoff: the item-read summary counts closed items from their front matter, so the closed share a store-design argument cites is the store's own, and the generator advisory counts a dropped item as a closure
verify: grep -q 'def test_the_summariser_reads_status_from_the_front_matter' tests/unit/test_item_read_log.py && grep -q 'def test_a_dropped_item_counts_as_a_closure' tests/unit/test_generator_check.py
---

**Problem.** Ten reads parse item front matter by hand instead of through docket.model, and one is wrong today: item_reads looks for status: done in a file's first 400 characters, so it reads 20 of 1,624 closed items as open; the others are generator_check's own parser, open-status set, list splits and a closure count that misses dropped, item_reads's --- split, and model's own parser restating FIELD_ORDER and LIST_FIELDS

**Sites**, from `PL-KGYT`'s sweep (its `**Swept 2026-10-01.**` line), each read against the source that day. Where a line says *agree*, the two spellings answer alike on every input today, and the risk is the next change to the fact reaching one of them only. `tools/item_reads.py:54` looks for `status: done` or `status: dropped` in a file's first 400 characters, and 20 of the 1,624 closed items put that line past it (measured 2026-10-01; `PL-WVSX`, `PL-ZZHZ`, `PL-HBH2` among them), so it reads them as open; `:75` splits the front matter on `---`. `tools/generator_check.py:187` is its own parser, whose reason, that a YAML dependency would stop it running from a bare checkout, does not reach `docket.model`, which is standard library; `:92` is its own open-status set (agrees); `:311`, `:318` and `:332` split list fields (agree); `:342` counts closures with `== "done"`, so a dropped member does not count. `subprojects/docket/src/docket/model.py:1423`'s `known` set restates `FIELD_ORDER` (the 26 keys are equal) and `:1457`-`:1475` restate `LIST_FIELDS`.

**Reproduced 2026-10-01** on `origin/main` `4eabd53`, reading all 1,921 item files through `item_reads.store()` and through `docket.model.parse_item`: 1,626 are closed and `store()` reads 1,607 as closed. It misses 20 (`PL-1BGP`, `PL-5MYR`, `PL-HBH2`, `PL-WVSX` and `PL-ZZHZ` among them), and it reads one open item as closed: this one, whose title quotes the words `status: done` inside the first 400 characters. The `---` split and `generator_check`'s parser agree with `docket.model` on every file, for every key that tool reads (`id`, `status`, `root-cause-of`, `touches`, `feature`).

**Why it matters.** `tools/item_reads.py` exists to measure what sessions do with the store (`PL-VV16`), and its second number is the share of opened items that are closed. A substring match over a window gets that share wrong both ways: an item whose status line falls past the window reads as open, and one whose prose quotes a status line reads as closed. The other nine sites agree today, and each is another parser that the next change to the item format has to reach.

**Done when.** `tools/item_reads.py` and `tools/generator_check.py` read every item through `docket.model` (`parse_item`, or `parse_front_matter` for a body), with no character window, `---` split, hand parser, open-status set or comma split of their own left. `generator_check` counts a closure with `CLOSED_STATUSES`, so a dropped item counts as one. `parse_item` takes its known keys from `FIELD_ORDER` and splits the fields `LIST_FIELDS` names. A regression test fails on the old `store()` (a closed status past 400 characters, and a title quoting `status: done`), and another on the old closure count.

**Generator check.** A member of `PL-KGYT` (spent), filed by that head's own sweep in the commit that closed it, so not a post-close instance; the fact is the head's: which spelling of a repeated predicate is the answer. Not `impairs-generators`: the one disagreement inside the generator machinery is the advisory's closure count, and the advisory ranks nothing. Counting dropped items moves its ratio column either way, since their children join the numerator as they join the denominator, and on this tree it changed no cluster's signals (measured 2026-10-01: the ratio moved on 21 of the 32 clusters with three open items, `src/anesthesia_sim/app` from 0.20 over 5 closed to 0.29 over 7).
