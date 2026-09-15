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
verify: grep -q 'covered_dirs' tests/unit/test_doc_check.py && ! grep -q 'no tree draws one today' docs/ARCHITECTURE.md && uv run pytest tests/unit/test_doc_check.py
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

**Its `verify:` was rewritten 2026-09-15, having turned `main` red (`PL-B5VM`).**
The command was `uv run pytest tests/unit/test_doc_check.py -k covered`. That
was honest when this item was captured — `-k covered` then matched no test, so
pytest exited 5 and the command failed, which is what an open item's command
must do. It did not stay honest: #593 (`PL-MXSL`, `PL-F933`, commit `7ba6108e`)
added `test_a_braced_citation_is_exempt_only_when_every_expansion_is_covered`,
a test about citations a `.gitignore` covers and nothing whatever to do with
`TreeMap.covered_dirs`. `-k` matched it on the substring, the command began
passing, and the whole-store `docket check --verify` on `main` reported this
item as work that had landed without being closed. None of its work had been
done — `covered_dirs` still appears nowhere in `tests/unit/test_doc_check.py`.

The replacement keys on both halves of "Done when" above rather than on a test
name: the test file must name `covered_dirs`, which only this item's work puts
there, and `docs/ARCHITECTURE.md` must no longer carry the "no tree draws one
today" clause this item is meant to replace. Confirmed failing on the tree as
found.

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

**Corrected 2026-09-15 (`PL-Y1W6`, after `PL-B5VM`).** Two findings about this
item's own text, neither of them its work. `PL-B5VM` fixed the second in `#598`
before this landed; the first is what this carries:

- The **Problem.** paragraph said "None is exercised by
  `tests/unit/test_doc_check.py`". That was false when written -
  `test_childless_directory_covers_its_whole_subtree` predates this item by
  months. Half of what this item asks for already exists, so the outstanding
  work is the negative direction and the `docs/ARCHITECTURE.md` prose, not a
  test from nothing.
- The `verify:` command was a bare `-k`, and `PL-B5VM` replaced it in `#598`.
  That half is landed; only the correction above arrives here.
