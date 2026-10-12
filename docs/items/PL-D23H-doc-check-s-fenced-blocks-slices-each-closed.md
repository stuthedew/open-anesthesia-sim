---
id: PL-D23H
title: doc_check's _fenced_blocks slices each closed fence to fences.Block.end, which is the fence's last content line where its list item or block quote closed it rather than a closing run, so that line is dropped from what the package-map tree and the other fenced-block readers read; fences.Block.body, recorded by PL-S4JL, is the reading to take; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-10-12
closed: 2026-10-12
pr: 1436
payoff: a fence its list item or block quote closes keeps its last line, so the package-map tree and the make-target reader see every line the fence holds
verify: grep -qF "a list item's fence its item's end closes" tests/unit/test_doc_check.py && ! grep -qF 'lines[block.start + 1 : block.end]' tools/doc_check.py
reenters: PL-R417
---

**Problem.** doc_check's _fenced_blocks slices each closed fence to fences.Block.end, which is the fence's last content line where its list item or block quote closed it rather than a closing run, so that line is dropped from what the package-map tree and the other fenced-block readers read; fences.Block.body, recorded by PL-S4JL, is the reading to take; latent

**Found 2026-10-12 in `PL-S4JL`'s fix.** `docket.fences.Block.end` is a
fence's closing line where its own run closed it, and its last content line
where the end of its list item or block quote did (CommonMark 0.31.2 § 4.5,
§ 5.2). `PL-S4JL` records which as `Block.closing` and gives the lines a block
holds as `Block.body`, and moved `tools/fixture_id_check.py` onto it.
`tools/doc_check.py`'s `_fenced_blocks` still slices
`lines[block.start + 1 : block.end]`, so it drops that last content line from
both its readers: the package-map tree `_check_package_map` reads and the `make`
targets `_make_mentions` reads from a fenced line.

**Reproduced 2026-10-12** on this branch, under the project's 3.14
interpreter: `_fenced_blocks("- item\n\n  ```text\n  a\n  b\nafter\n")`
gives `[(3, ['  a'])]`, where the same fence closed by its own run gives
`[(3, ['  a', '  b'])]`. Latent: none of the 2,616 tracked Markdown files
holds a fence its container closes.

**Generator check, added at closure 2026-10-12.** The same form as
`PL-S4JL`'s fence join, a container-closed fence's last line, which that
item's triage placed under `PL-R417`: where one statement ends, in a format
that continues one across lines. Filed after that head closed on 2026-10-11,
so it records `reenters: PL-R417`; latent, so it stays an ordinary item under
the head's `spent` verdict rather than reopening it. The fix reads the record
`PL-S4JL` added, `fences.Block.body`, rather than a second reading of
`Block.end`, and came with `PL-5M36`'s change to the same function.

**Why it matters.** A `make` target named on the last line of such a fence
goes unchecked while `make check` passes, and a package map written that way
loses its last entry.

**Done when.** `_fenced_blocks` reads each block's lines through
`fences.Block.body`, and a test pins a container-closed fence's last line.
