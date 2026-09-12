---
id: PL-0M7L
title: _resolves raises ValueError on a '**' token and NotImplementedError on an absolute-looking path, so doc_check aborts instead of reporting a citation
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.4.14
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-07
closed: 2026-09-12
pr: 496
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_an_absolute_glob_citation_is_reported_rather_than_raised' tests/unit/test_doc_check.py
---

**Problem.** _resolves raises ValueError on a '**' token and NotImplementedError on an absolute-looking path, so doc_check aborts instead of reporting a citation

`_resolves` (`tools/doc_check.py:1416`) passes the cited token straight to
`Path.glob`, which raises rather than returning nothing for two token shapes
that appear in this repository's prose:

- `ValueError: '**' can only be an entire path component` - from a token such
  as `docs/**.md` written as an illustrative pattern.
- `NotImplementedError: Non-relative patterns are unsupported` - from a token
  that begins with `/`, such as `/docs/worker.md`.

Both abort `python3 tools/doc_check.py check` with a traceback instead of
reporting a citation, so the whole documentation gate stops rather than
failing on the one line. Neither is reachable from the files `DOC_GLOBS`
collects today; both were reached immediately on 2026-09-07 by a probe that
read `docs/items/*.md` and `.py` docstrings while working `PL-X2XX`, so any
widening of the citation input hits them first.

A cited token that `glob` cannot parse is a citation that does not resolve,
not a reason to stop: catch both and report the line.

**Why it matters.** A citation that cannot be parsed should be *reported*; here
it aborts the run. `python3 tools/doc_check.py check` exits on a traceback, so
the documentation gate reports nothing at all about the other several hundred
citations in the tree - one malformed token takes the whole check offline, and
the failure looks like a broken tool rather than a finding about a line.

Re-measured 2026-09-12 against this project's own interpreter (3.14), which
narrows the item without removing it: `docs/**.md` no longer raises, and a bare
`/docs/worker.md` never reaches `glob` because it is not treated as a pattern.
What still raises is an absolute token that *is* a pattern - `/docs/*.md` -
which gives `NotImplementedError: Non-relative patterns are unsupported`. The
narrowing is worth recording because it changes the test the fix owes: the
regression case is an absolute pattern, not the two originally written down.

**Done when.** `_resolves` returns "does not resolve" for a token `glob` refuses
to parse instead of propagating the exception, `doc_check check` reports that
citation as unresolved and completes the rest of the run, and a test covers an
absolute glob token.
