---
id: PL-DMDF
title: docket digest asks one git diff per item file because _superseded is called with a one-element tuple inside a loop, where the function already takes the whole set
priority: P2
effort: S
status: ready
classes: perf, defect
feature: session-start-cost
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests
added: 2026-09-16
verify: uv run pytest -q subprojects/docket/tests/test_vcs.py && grep -q 'def test_superseded_is_asked_once_for_the_whole_outstanding_set' subprojects/docket/tests/test_vcs.py
---

**Problem.** docket digest asks one git diff per item file because _superseded is called with a one-element tuple inside a loop, where the function already takes the whole set

**Found while working `PL-XD3C`, and it is larger than any of the three items
that session was given.** `_superseded` in `subprojects/docket/src/docket/vcs.py`
takes `paths: tuple[str, ...]` and passes them to git as one pathspec - and its
caller at line 3619 does exactly that, handing over the whole outstanding set.
The caller inside `branches_in_flight` does not. It is a dict comprehension that
calls the function once per item, with a one-element tuple:

```python
and path not in _superseded(name, base, (path,), root, run)
```

So one `git diff --numstat --no-renames <base> <ref> -- <one item file>` runs for
every item file edited on every unmerged ref. On this container that is 135 of
the 159 `diff` calls the command makes.

**Measured, not inferred.** A scratch clone of this repository was given a
fabricated ref set of a known size - the point being that the original
investigation compared two machines whose ref sets differed and had moved hours
apart, so its ratio was attributable to nothing. Holding the ref count fixed and
varying the commits, then holding the commits fixed and varying the refs,
separates the drivers:

| subcommand | per unmerged ref | per item file a ref introduces |
| --- | --- | --- |
| `merge-base` | 3.0 | 0 |
| `show` | 0 | 1.0 |
| `diff` | ~4.0 | ~0.95 |

At 30 unmerged refs carrying 390 item edits - chosen to match the owner's clone,
and it does: 1,237 calls against their 1,107, `diff` 593 against 570, `show` 446
against 389, `merge-base` 90 against their 78, which is exactly 3 x their 26
unmerged refs - hoisting the call out of the comprehension gives:

| | before | after |
| --- | --- | --- |
| `diff` calls | 593 | **148** |
| total git calls | 1,237 | **792** |

**The fix is a loop hoist and nothing else.** Group the candidate paths by ref,
ask `_superseded` once per ref, then filter against what comes back. The
function's own parsing is unchanged, because a multi-path pathspec is the shape
it was written for: git names every path it was given that differs, which is the
property the "absent from the diff means the tips agree" branch already relies
on. Prototyped on the scratch clone: `digest` output byte-identical, all 1,007
docket tests passing.

**Why it is filed rather than done.** It is a fourth change, in the same file as
`PL-XD3C`, `PL-0J9K` and `PL-MMVF`, and larger than two of them. `CLAUDE.md`
asks the owner before a deliverable differs materially from the one described,
and the brief scoped `diff` to being *measured* rather than fixed.

**One thing to decide with it.** The pathspec grows with the items a single ref
touches. A triage-pass branch touching several hundred item files would build a
long command line - roughly 60 bytes a path, so ~35 KB at 600 paths, against a
2 MB `ARG_MAX` on Linux and 256 KB on macOS. It fits today and would want
chunking before it did not; the alternative is dropping the pathspec entirely and
filtering git's full output in Python, which removes the limit but changes the
contract `_superseded`'s docstring reasons about.

**Done when** `branches_in_flight` asks `_superseded` once per unmerged ref
rather than once per item file, the digest's output is byte-identical, a test
pins that a ref with several outstanding paths is answered in one call, and this
item records the re-measured `diff` count on the owner's clone.

**Independently quantified.** A separate pass reading the call graph put this
site at 25 of the container's 87 `diff` calls and **at least 440 of the owner's
570**, reached from the `walk.edited` comprehension at `vcs.py:1283`. That agrees
with the prototype measured here from the other direction - 593 to 148, a saving
of 445 - which is the closest thing to confirmation this question has had.

**Why it matters.** It is the largest single block left in `docket digest` after
`PL-XD3C`'s ref work, and unlike the other three items in that measurement it is
a one-line hoist rather than a redesign: `_superseded` already takes the whole
set, and its sibling caller at line 3619 already passes it that way. The cost is
paid at every session start, on every machine, for a call shape the same file
elsewhere gets right.

It also compounds with the ref count rather than merely adding to it. `diff` runs
at roughly 4.0 per unmerged ref *plus* 0.95 per item file a ref introduces, so
the per-file term grows as branches accumulate item edits - the normal state of
this store, where a capture or a triage pass edits item files and nothing else.

---

**Decided: chunk the pathspec** (project owner, 2026-09-17, ratified). Chosen
over dropping the pathspec and filtering git's full output in Python, which
removes the `ARG_MAX` ceiling but changes the contract `_superseded`'s docstring
reasons about — "git names every path it was given that differs" is the property
the "absent from the diff means the tips agree" branch relies on, and filtering
in Python means re-deriving that property in a second place. Chunking keeps the
contract and confines the change to the call site, which is what the brief above
already scoped.

Ratified rather than specified: this was a session's recommendation, so
`CLAUDE.md`'s reopening bar is the lower one — a measurement, or a cost the case
did not carry, is enough to put it back to the owner.

**Two things to settle while implementing, neither of them reopening the above.**
The chunk size is not stated here on purpose: ~60 bytes a path against a 2 MB
`ARG_MAX` on Linux and 256 KB on macOS means macOS is the binding constraint, so
size the chunk against that rather than against the platform the session runs on.
And a chunked `_superseded` is called more than once per ref, so whatever the
loop hoist saves must be re-measured after chunking rather than quoted from the
593 → 148 figure above, which was measured unchunked.

**Scope correction, verified 2026-09-17 against `origin/main`.** This item was
recommended as one of a four-item `vcs.py` branch with `PL-0J9K`, `PL-MMVF` and
`PL-XD3C`. Two of those three had already landed in `#635` (`ff4be61`): `git
cat-file --batch` is at `subprojects/docket/src/docket/vcs.py:313` (`PL-0J9K`)
and `GitRunner`'s memo is at `vcs.py:174` (`PL-MMVF`). Their item files were
left at `status: untriaged` by that commit, which is why they still read as
open. The live branch is therefore this item plus `PL-XD3C`, not four.
