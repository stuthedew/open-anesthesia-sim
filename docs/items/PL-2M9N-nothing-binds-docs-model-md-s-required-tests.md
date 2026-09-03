---
id: PL-2M9N
title: Nothing binds docs/MODEL.md's 'Required tests' headings to the tests that satisfy them
priority: P3
effort: M
status: ready
classes: test, infra
feature: model-spec-accuracy
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/MODEL.md
added: 2026-09-03
verify: python3 tools/doc_check.py check && uv run pytest tests/unit/test_doc_check.py && grep -q 'def check_required_tests' tools/doc_check.py
---

**Problem.** `docs/MODEL.md` § "Required tests" carries fifteen `###` headings,
each specifying a test the implementation must have. Nothing maps a heading to
a test. `tools/doc_check.py` decides the package-map, provenance-table,
marked-prose-value, dangling-citation, math-rendering and release-train
questions, and `check_citations()` resolves cited paths, links and headings -
but a heading that names a *test* resolves to nothing, so a required test can
be never written, deleted, or renamed and every gate stays green.

It already has been: `PL-GZP6` records two of the fifteen that were never
implemented, found by reading the section against the suite by hand in an
audit rather than by anything that runs.

**Why it matters.** This is the shape `CLAUDE.md`'s deterministic-tooling
section is about. "Does a test exist that claims to satisfy this heading" is
answerable by reading the tree, is asked every time the section changes, and
is currently answered by a session spending context on it - which is the
expensive tier, and which happened once in nine months. Whether the test is
*adequate* is judgment and must stay judgment; that line is exactly the one
`tools/doc_check.py` already draws when it decides a cited path exists without
deciding the sentence around it is true.

The safety argument is the same one the file's docstring makes about stale
documentation: a specification stating fifteen "must"s of which thirteen hold
is a document a reader trusts further than it has earned.

**Where.** `docs/MODEL.md:923-1308`; `tools/doc_check.py` (alongside
`check_citations`, `:1379`); `tests/unit/test_doc_check.py`.

**Approach.** A `check_required_tests()` in `tools/doc_check.py`, standard
library only, wired into `check`:

1. Parse the `###` headings under `## Required tests`.
2. Require each to name the test or module that satisfies it, in a marked form
   the checker can find - a backticked `tests/...` path plus a `test_` name is
   the cheapest, and matches how the sections already cite the suite in prose.
3. Resolve each with `ast`, the way `test_oracle_imports_no_solver_from_core`
   resolves its own imports: the file must exist and must define a function of
   that name. Do not run the test; existence is the decidable half.

The marking has to be added to the thirteen sections that already have tests,
which is most of the work and is also the audit that catches any further
mismatch. `PL-GZP6` is the two that will not resolve.

**Deliberately not decided here:** whether an unsatisfied heading is an error
or an advisory. `CLAUDE.md` reserves hard failure for exact rules, and "this
heading names no test" is exact - but a section deliberately specifying a test
for a future milestone would then fail the build. Resolve it when the thirteen
are marked and it is clear whether any such section exists.

**Done when.** `python3 tools/doc_check.py check` reports every `### ...test`
heading under `## Required tests` that does not resolve to a test function that
exists, and `tests/unit/test_doc_check.py` covers a heading that resolves, one
that names a missing function, and one that names a missing file.
