---
id: PL-0M7L
title: _resolves raises ValueError on a '**' token and NotImplementedError on an absolute-looking path, so doc_check aborts instead of reporting a citation
status: untriaged
added: 2026-09-07
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
