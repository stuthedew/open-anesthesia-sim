---
id: PL-0J9K
title: Replace docket's per-blob git show fan-out with one git cat-file --batch: 389 processes and 5.77s of a 24s session start on the owner's machine
status: untriaged
added: 2026-09-16
---

**Problem.** Replace docket's per-blob git show fan-out with one git cat-file --batch: 389 processes and 5.77s of a 24s session start on the owner's machine

**Problem.** `subprojects/docket/src/docket/vcs.py` reads a committed blob by
spawning `git show <rev>:<path>`, one process per blob, at seven call sites -
lines 926, 1075, 2165, 2552, 2802, 3069 and 3191 - most of them inside a loop
over item files. Measured 2026-09-16 on the same commit and store:

| | session container | owner's macOS clone |
| --- | --- | --- |
| `show` calls per `docket digest` | 18 | **389** |
| time in `show` | 0.05 s | **5.77 s** |
| share of the whole `digest` | 2% | **24%** |

**The fix is the standard one and changes no semantics.** `git cat-file --batch`
takes `<rev>:<path>` lines on stdin and returns every blob from a single
process. 389 spawns become 1. The bytes are identical - it is the same object
lookup - so no caller's behaviour changes and no output moves.

**Two things to get right.** A missing path makes `cat-file --batch` print
`<spec> missing` on stdout rather than failing, where `git show` exits non-zero;
whatever `vcs.py` does today with a blob that is absent at that rev has to keep
happening, and that is the behaviour the test should pin. And the batch process
has to be scoped to one command and closed, for the reason `PL-MMVF` gives about
a cache outliving a fetch.

**Why this one first.** It is the largest single block after `diff`, it is a
mechanical substitution against a documented git interface, and unlike `PL-XD3C`
it needs no design round. Sequenced after `PL-XD3C`'s ref count is verified,
because if the ref count turns out not to be the driver then these 389 calls
were never going to be 389.

**Done when** `docket digest` spawns one `cat-file` process where it now spawns
one `show` per blob, the digest's output is byte-identical on both machines, the
missing-blob path is covered by a test, and the item records the re-measured
`show` time on the owner's clone.
