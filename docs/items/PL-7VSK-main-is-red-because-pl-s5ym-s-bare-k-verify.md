---
id: PL-7VSK
title: main is red because PL-S5YM's bare -k verify command started passing on an unrelated test #593 added, and docket check --verify runs only in CI so make check cannot see it
status: dropped
reason: PL-B5VM reached the same diagnosis and the same repair and merged first, as #598
priority: P2
effort: S
classes: defect
touches: docs/items
added: 2026-09-15
closed: 2026-09-15
---

**Problem.** main is red because PL-S5YM's bare -k verify command started passing on an unrelated test #593 added, and docket check --verify runs only in CI so make check cannot see it

**Why it matters.** `main` went red on `7ba6108e` (`#593`) and nothing surfaces
it: `quality.yml` runs on `push` to `main`, so no pull request shows the
failure, and the session that merged `#593` had already moved on. Two further
merges - `#594` and `#596` - landed on top of a red base without anyone
learning it was red.

The failure was real rather than noise. `docket check --verify` errored that
`PL-S5YM` is open while its `verify:` command already passes, and the error
states its own consequence: `bin/docket verify` would ACCEPT a branch that did
none of `PL-S5YM`'s work. A gate that admits unfinished work while reporting
success is `CLAUDE.md`'s first compounding-friction test - a check passing while
the guarantee it stands for is void.

**The mechanism, reproduced rather than inferred.** `PL-S5YM`'s command was
`uv run pytest tests/unit/test_doc_check.py -k covered`, written before
`verify:` commands were required to be run. It is the bare `-k` the `docket`
skill names outright: with nothing matching, `pytest` selects nothing and exits
5, which reads as a command correctly failing while specifying only that some
test somewhere come to be called something containing "covered".

`#593` added seven tests to that file. One of them -
`test_a_braced_citation_is_exempt_only_when_every_expansion_is_covered`, about
path citations `.gitignore` covers - shares nothing with `PL-S5YM` but the
substring. `-k covered` selected it and passed:

```
$ uv run pytest tests/unit/test_doc_check.py -k covered --collect-only -q
tests/unit/test_doc_check.py::test_a_braced_citation_is_exempt_only_when_every_expansion_is_covered
1/235 tests collected (234 deselected)
```

`#593` is not at fault. It added a correctly named test to a file it owned;
what broke was a command in an unrelated item that had never been able to
discriminate.

**Why `make check` could not catch it.** `make check` runs `bin/docket check`;
only CI passes `--verify`. The skill already records that asymmetry - "CI is
what passes that flag, so this is caught after the item is written *and* after
it is pushed" - and this is that gap arriving with a red `main` at the end of
it rather than an advisory.

**What was done.** `PL-S5YM`'s `verify:` was repaired to the paired shape the
skill prescribes, and the reasoning written into that item so the next session
reading it does not re-derive this. The item itself is untouched and still
open: its work - testing `TreeMap.covered_dirs` in both directions - remains
undone, which is exactly what the repaired command now says.

**Deliberately not done here.** Making `make check` run `--verify` too. It is
147 commands in 150 s wall-clock against a 1 031 s serial total, which is a
real cost on a gate run before every commit, and whether to pay it is a
judgement about how the project is worked rather than a defect to fix under a
red `main`. Captured separately as `PL-MR6S` so the question reaches the owner
as a decision rather than riding in on a hotfix.

**Dropped 2026-09-15: `PL-B5VM` got there first.** Three sessions reached this
red `main` independently - `PL-99YZ`, already on `main`, is the item recording
that. `PL-B5VM` merged as `#598` while this branch was open, carrying the same
diagnosis (a bare `pytest -k covered` flipped to passing by an unrelated test
`#593` added) and the same repair, so the merge of `origin/main` into this
branch conflicted on exactly the one file both had rewritten.

**Resolved to `PL-B5VM`'s version, and it is the better command.** Where this
item's replacement named one test the work must create, theirs holds both
halves of `PL-S5YM`'s own `Done when.` without dictating any name:

```
grep -q 'covered_dirs' tests/unit/test_doc_check.py
  && ! grep -q 'no tree draws one today' docs/ARCHITECTURE.md
  && uv run pytest tests/unit/test_doc_check.py
```

The second clause is the part this item missed - `docs/ARCHITECTURE.md` still
claims no tree draws a bare directory, and that claim has to go with the work.

`PL-B5VM` also captured the general case as `PL-Q8RQ`: four open items rest on
a bare `-k`, and whether a command can discriminate at all is decidable enough
for `docket check` to refuse it. That is the durable fix and this item never
reached it.

