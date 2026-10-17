---
id: PL-LYH3
title: tools/doc_check.py's analyze() reads the item store seven times in one run (16,009 parse_item calls for about 2,300 items, via _read_store), about 10.6 s of a 59 s profiled whole-repository analysis on 2026-10-17, and a quality.yml checks job runs that analysis five times (the two doc_check.py check steps and three tests in tests/unit/test_doc_check.py), so reading the store once per analysis would cut each run by roughly a sixth (found working PL-H9KW)
priority: P2
effort: S
status: ready
classes: perf
feature: ci-cost
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/WORKING_NOTES.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-17
payoff: each whole-repository documentation check parses the item store once instead of seven times, about 1.7 s less per analysis and 5 to 8.5 s less per CI checks job
verify: grep -q 'def test_one_analysis_reads_the_item_store_once' tests/unit/test_doc_check.py
---

**Problem.** `tools/doc_check.py`'s `analyze()` reads the item store seven
times in one run, and each read parses every item file. Five checks call
`_read_store` for themselves, and so does `_live_item_briefs`, which three more
checks call. Nothing shares the first read with the others.

**Reproduced 2026-10-17**, without a profiler, at `9ca5290b`. One `analyze()`
of this repository called `_read_store` 7 times and `parse_item` 16,289 times
for 2,327 items. The reads took 2.0 s of the 32.4 s run. The title's 10.6 s of
59 s came from a profiled run, and a profiler adds a cost to every call, which
inflates a function called 16,000 times. So one shared read saves about 1.7 s
of each analysis, about 5% rather than the title's sixth.

**Why it matters.** Every whole-repository analysis pays this cost. The
`checks` job in `quality.yml` runs two: `python3 tools/doc_check.py check` on
the bare interpreter, and `uv run python tools/doc_check.py check` after the uv
install. The three tests that read the real tree add one analysis in each
pytest worker that runs one of them, since `PL-H9KW` cached that report per
process. That is three to five analyses per job, about 5 to 8.5 s at this
container's speed. Every local `make check` pays it once more.

**Done when.** One `analyze()` run reads the store once, and the next run reads
it again. `test_one_analysis_reads_the_item_store_once` in
`tests/unit/test_doc_check.py` counts the `read_items` calls over two analyses
of a fixture repository and asserts one for each. A check called on its own,
outside `analyze()`, still reads the store from disk.

**Generator check.** A one-off. `PL-R0P3` made `_read_store` the one spelling
of the store read, which settled what the read returns but not how often it
runs. Every read returns the same thing, so no reader misreads a fact, and no
head's `misread:` line is about a repeated cost.
