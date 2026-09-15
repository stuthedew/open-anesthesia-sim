---
id: PL-S5YM
title: doc_check's covered-directory branch now has no instance in any tree and no test
priority: P3
effort: S
status: ready
classes: test, infra
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/ARCHITECTURE.md
added: 2026-08-30
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_a_bare_directory_in_the_package_map_covers_the_files_beneath_it' tests/unit/test_doc_check.py
---

**Problem.** `TreeMap.covered_dirs` in `tools/doc_check.py` handles a directory
drawn in a `docs/ARCHITECTURE.md` package-map tree with no children beneath it:
the entry stands for its whole subtree, so files under it are covered without
being listed. Three code paths implement it (`TreeMap.covered_dirs`,
`TreeMap.entries`, and the parent walk in the disk-vs-map comparison). None is
exercised by `tests/unit/test_doc_check.py`, and as of PL-STNV none is
exercised by the trees either — `tools/review-verification/` was the only bare
directory any tree drew, and it is gone.

**Why it matters.** `tools/doc_check.py` gates every documentation change in
CI, and this branch decides whether a file counts as mapped. Untested and with
no live instance, it is the shape that quietly stops working: the next session
to draw a bare directory would find out from a false failure, or worse from a
false pass that lets an unmapped module through. It is also the case
`docs/ARCHITECTURE.md` still documents in prose, so the tree says the feature
exists while nothing demonstrates that it does.

Low urgency — no clinical value is reached by any of it, and `make check` is
green either way.

**Where.** `tools/doc_check.py:196-212` (`TreeMap`), `:312` (construction),
`:356` (the parent walk); `tests/unit/test_doc_check.py`;
`docs/ARCHITECTURE.md`'s "Developer tooling (`tools/`)" section, which
currently says "no tree draws one today".

**Approach — test it rather than delete it.** The mechanism is right: a
subtree documented by its own README should be mapped as one unit rather than
module by module, and `subprojects/` is the obvious next thing to be drawn that
way. So add a unit test that builds a tree with a bare directory and asserts
both directions — a file beneath it counts as mapped, and a file outside it
still fails. Deleting the branch instead would be the cheaper change today and
the wrong one, since the prose would have to go with it and the capability
would be rebuilt the next time a subtree needs it.

**Done when.** `tests/unit/test_doc_check.py` covers the covered-directory
branch in both directions, and `docs/ARCHITECTURE.md`'s claim about it names
the test rather than noting that no tree uses it.

**`verify:` repaired 2026-09-15 under `PL-7VSK`; the item itself is untouched
and still open.** The command was `uv run pytest tests/unit/test_doc_check.py
-k covered`, which is the bare `-k` the `docket` skill warns about: with no
test matching, `pytest` selects nothing and exits 5, so it *looked* like a
command failing as intended while specifying only that some test somewhere come
to be called something containing "covered".

`#593` then added
`test_a_braced_citation_is_exempt_only_when_every_expansion_is_covered` - a
test about path citations `.gitignore` covers, sharing nothing with this item
but the substring. `-k covered` selected it, the command passed, and
`docket check --verify` correctly errored that an open item's command already
passes. That error is what turned `main` red on `7ba6108e`, and it was right:
`bin/docket verify` would have accepted a branch that did none of this item's
work.

Replaced with the paired shape - the file's whole suite, plus a `grep` for the
test this item owes - which exits 1 before the work and cannot be satisfied by
an unrelated test's name. The test name is this item's `Approach` written out:
a bare directory in the package map covers the files beneath it. The second
direction the brief asks for, that a file *outside* it still fails, stays a
`Done when.` requirement rather than a second `grep`, so the command specifies
the work without dictating what its guard is called.

