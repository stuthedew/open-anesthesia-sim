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
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_a_file_outside_a_childless_directory_still_needs_a_line' tests/unit/test_doc_check.py
---

**Problem.** `TreeMap.covered_dirs` in `tools/doc_check.py` handles a directory
drawn in a `docs/ARCHITECTURE.md` package-map tree with no children beneath it:
the entry stands for its whole subtree, so files under it are covered without
being listed. Three code paths implement it (`TreeMap.covered_dirs`,
`TreeMap.entries`, and the parent walk in the disk-vs-map comparison).
`tests/unit/test_doc_check.py` exercises them in **one direction only**:
`test_childless_directory_covers_its_whole_subtree` (line 208, there since
`PL-032`) asserts that a file *beneath* a childless directory needs no line,
against a fixture whose tree draws `harness/` bare with `run.py` under it.
Nothing asserts the other direction - that a file *outside* one still fails.
As of PL-STNV none is exercised by the trees either — `tools/review-verification/` was the only bare
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

**Corrected 2026-09-15 (`PL-Y1W6`).** Two repairs, neither of them this item's
own work:

- The **Problem.** paragraph said "None is exercised by
  `tests/unit/test_doc_check.py`". That was false when written -
  `test_childless_directory_covers_its_whole_subtree` predates this item by
  months. Half of what this item asks for already exists, so the outstanding
  work is the negative direction and the `docs/ARCHITECTURE.md` prose, not a
  test from nothing.
- The `verify:` command was `uv run pytest tests/unit/test_doc_check.py -k
  covered`, a bare `-k`. `#593` added
  `test_a_braced_citation_is_exempt_only_when_every_expansion_is_covered`;
  `-k` matches substrings, so the selector began matching a braced-citation
  test with nothing to do with this item, selected it, passed, and turned
  `main` red on `docket check --verify`. Replaced with the paired shape the
  `docket` skill prescribes - the file's whole suite, which proves it healthy,
  and a `grep` naming the exact test this item owes.
