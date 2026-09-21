---
id: PL-DMDF
title: docket digest asks one git diff per item file because _superseded is called with a one-element tuple inside a loop, where the function already takes the whole set
priority: P2
effort: S
status: done
classes: perf, defect
feature: session-start-cost
milestone: v0.4.28
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests
added: 2026-09-16
closed: 2026-09-17
pr: 664
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

**Done, 2026-09-17.** `branches_in_flight` collects the candidate `(id, ref,
path)` marks in one pass over `walk.edited`, groups their paths by ref, and
asks `_superseded` once per ref. Nothing else about the read changed: the two
cheap filters are applied before the grouping, `walk.edited`'s order is kept so
the report is assembled in the order the walk found the ids, and each path is
still judged on its own row of the answer.

**Measured on this container, against a ref set that did not move between the
two runs** - the defect `PL-XD3C` records, where a 5x ratio was attributed to
three different scaling laws because the two sides were counted hours apart.
Both runs are `bin/docket digest --profile` on the same checkout, one with
`vcs.py` from `HEAD` and one with the change, at 25 refs, 6 merged, 19
unmerged, carrying 30 commits and 111 item-file edits:

| | before | after |
| --- | --- | --- |
| `diff` asked | 155 | **92** |
| `diff` run | 115 | **54** |
| git calls asked | 348 | **285** |
| git processes spawned | 179 | **118** |
| seconds in git | 0.93 | **0.69** |

`bin/docket digest`'s output is byte-identical between the two, diffed rather
than eyeballed.

**The saving is bigger where the store is, and this container is the wrong
place to read it from.** `diff` runs at ~4.0 per unmerged ref plus ~0.95 per
item file a ref introduces, and only the second term is what the hoist
removes - so a container carrying 111 item edits sees 61 fewer processes where
the fabricated 30-ref, 390-edit store predicted 445. What the *tests* pin is
the call shape rather than the saving, because the shape is a property of the
code and the saving is a property of the ref set.

**The pathspec-length question the brief left open is decided: split, and split
on bytes.** Not because the command line would otherwise be too long - it would
not, at ~60 bytes a path against the 2,097,152 `getconf ARG_MAX` reports here -
but because of what happens if it ever were. `subprocess` raises on an
over-long argv, `_run_git` turns that into the empty string, and a `--numstat`
naming no paths is read as "the tips agree about every one of them", so every
in-flight mark the ref carries would be dropped silently. That is the direction
`_superseded`'s own docstring says it must never fail in, and the hoist is what
would make one failure cost a whole ref rather than one path. `_pathspec_chunks`
bounds it at 64 KiB - about a thousand queue paths, so no branch in this store's
history reaches a second chunk - and each chunk's absences are read against that
chunk alone, since "git did not name this path" means "the tips agree" only
about paths that call actually asked for.

The alternative the brief named - dropping the pathspec and filtering git's
whole-tree output in Python - was refused for cost rather than contract. The
inference survives it (a path absent from an unfiltered `--numstat` has
identical content on both tips, exactly as before), but it makes every call
parse the branch's entire diff to answer a question about its item files, which
on a branch carrying a Qt port is thousands of rows for a handful of answers.

**Five tests, each shown to fail against the code it pins.** Reverting the
hoist alone fails `test_superseded_is_asked_once_for_the_whole_outstanding_set`
and `test_two_refs_are_asked_separately_and_each_about_only_its_own_paths` and
nothing else; raising `_PATHSPEC_BYTES` by 1024x fails the two splitting tests;
reading a chunk's answer against the whole set rather than against the chunk
fails `test_a_split_pathspec_answers_every_path_it_was_given`.

**What this did not fix, and it is now filed.** The empty-output reading above
is only *newly dangerous* here; it was already wrong. `_superseded`'s docstring
claims all three of its silences leave a path outstanding, and two of them do
the opposite. `PL-Q9Z1` carries it, with the two routes to a fix and why
neither is a fix-now.

**The re-measured `diff` count on the project owner's clone is still owed**, and
it is the same single command `PL-XD3C` (digest is O(unmerged refs)) already
owes - `bin/docket digest --profile` run there, compared against a container's
`ref set` block before any count is compared. Held by that item alone rather
than by two.

---

**Measured on the project owner's clone, 2026-09-17, and it is the largest
single saving this lane has produced.** Both runs are `bin/docket digest
--profile` on that machine, before and after the hoist, against a ref set that
did not move between them - 38 refs, 5 merged, 33 unmerged, carrying ~2,270
commits and ~1,284 item-file edits (the two runs differ by 3 commits and 1 edit,
0.1%, from other sessions pushing in between):

| | before | after | change |
| --- | --- | --- | --- |
| `diff` asked | 654 | 161 | -75% |
| `diff` processes | 586 | 95 | -84% |
| `diff` seconds | 9.76 | **1.63** | **-8.13 s** |
| git calls asked | 1,245 | 755 | -39% |
| git processes | 689 | 198 | -71% |
| git seconds | 11.72 | **3.61** | **-8.11 s** |

**Every other subcommand is flat, which is the control rather than a footnote**:
`ls-tree` 40 to 40, `merge-base` 33 to 33, `log` 17 to 17, `show` 373 to 376,
`rev-parse` 9 to 9, `rev-list` 1 to 1, `for-each-ref` 2 to 2. The only
subcommand that moved is the only one this change touches. The folded-read
counts are unmoved too - the memo 184 to 182, the blob batch 372 to 375 - so
`PL-MMVF` and `PL-0J9K` are neither helped nor harmed by it; the "73% fewer
processes" line reads better than the earlier "44%" only because its
denominator shrank.

**The fabricated-store experiment predicted the ratio to within 1%.** It was
run on a scratch clone given ref sets of known size, varying commits with refs
held fixed and then the reverse, and it predicted `diff` would fall 4.01x and
the whole command 36%. On the real machine `diff` fell **4.06x** and the whole
command **39%**. Given that this item's feature had three scaling models
refuted in one sitting (`PL-XD3C`), a controlled synthetic that predicts the
real machine this closely is the finding about method, not only about `diff`.

**Where the laws did mis-predict is the absolute per-item-edit slope**, by
about 2x: 0.95 per item-file edit against 1,284 edits predicts ~1,353 `diff`
calls before the hoist, and the machine made 654. The cause is a units
mismatch in `--profile`'s own `ref set` block rather than in the law -
`PL-3BYK` carries it - and it does not touch the before/after numbers above,
which are measured rather than derived.

**Both obligations this item and `PL-XD3C` were carrying are now met**, from
this one run: the re-measured `diff` count is above, and `PL-0J9K`'s re-measured
`show` time on the same clone is 412 asked, 376 reaching git, 375 of them folded
into one `cat-file --batch` - **0.06 s, against the 5.77 s that item measured
before the batch existed.**

**Recovered 2026-09-21 from `claude/amazing-thompson-3hwksq`** (`PL-DZM1`), a
branch with no open pull request that has since been deleted from the remote —
its only surviving copy was one container's unpruned remote-tracking ref. The
decision below was ratified while this item was open, shipped in `#664`, and
never reached `main` in writing. It is appended after close because it is
provenance for live code rather than a change to what closed the item:
`_pathspec_chunks` at `subprojects/docket/src/docket/vcs.py:1330` is the design
it chose, and a later session proposing the rejected alternative would find
nothing on `main` saying it had already been weighed.

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

**Two things settled while implementing, neither of them reopening the above.**
The chunk size was not stated in the decision on purpose: ~60 bytes a path
against a 2 MB `ARG_MAX` on Linux and 256 KB on macOS means macOS is the binding
constraint, so the chunk was sized against that rather than against the platform
the session ran on. And a chunked `_superseded` is called more than once per
ref, so what the loop hoist saves was re-measured after chunking rather than
quoted from the 593 → 148 figure above, which was measured unchunked.

**Scope correction, verified 2026-09-17 against `origin/main`.** This item was
recommended as one of a four-item `vcs.py` branch with `PL-0J9K`, `PL-MMVF` and
`PL-XD3C`. Two of those three had already landed in `#635` (`ff4be61`): `git
cat-file --batch` is at `subprojects/docket/src/docket/vcs.py:313` (`PL-0J9K`)
and `GitRunner`'s memo is at `vcs.py:174` (`PL-MMVF`). Their item files were
left at `status: untriaged` by that commit, which is why they still read as
open. The live branch was therefore this item plus `PL-XD3C`, not four.
