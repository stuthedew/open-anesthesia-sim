---
id: PL-QSJM
title: "make check's ruff passes where CI fails after a module is deleted: ruff's cache keys a result to the linted file's mtime alone, so a first-party import that no longer resolves keeps its stale verdict"
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.4.26
touches: Makefile, tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-15
closed: 2026-09-15
pr: 590
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'ruff check --no-cache' Makefile
---

**Problem.** `make check`'s ruff passes where CI fails after a first-party
module is deleted. The cause is ruff's own result cache, not `__pycache__`:
this item was filed blaming stale bytecode and that was wrong. See the
correction below before reading the original evidence as fact.

**Evidence, 2026-09-15 (PL-25KS, #588).** The port deleted
`src/anesthesia_sim/app/chart_series.py`. `spikes/qt/qt_spike.py` and
`spikes/qt/chart_sources.py` still imported a constant from it. CI's
`uv run ruff check .` reported both import blocks unsorted (I001). The local
`make check` on the same tree passed.

**Correction, 2026-09-15: `__pycache__` had nothing to do with it.** The item
asked for the mechanism to be measured before a fix named it, and the
measurement refuted the mechanism. On ruff 0.16.4, holding everything else
fixed:

| tree state | `.pyc` present | `.ruff_cache` | ruff says |
| --- | --- | --- | --- |
| module deleted | yes | warm | `All checks passed!` |
| module deleted | **no** | warm | `All checks passed!` |
| module deleted | yes | **cold** | the `I001`s |
| module deleted | no | **cold** | the `I001`s |

The `.pyc` is inert in both directions; the cache decides the answer alone.
Replayed against the real tree at `abf855b2`: warm cache plus the delete gives
`All checks passed!`, and `rm -rf .ruff_cache` on that same tree gives the two
`I001`s CI reported, plus two more in `tests/` the port also had to fix.

**Why the original experiment pointed at the `.pyc`.** It changed two things
at once. "Removing that file and re-running ruff on the original imports"
rewrote the importing files to restore the `chart_series` import — and ruff's
`FileCacheKey` is the linted file's **mtime and permission bits, and nothing
else**, so rewriting the file is what invalidated its entry. Confirmed by
separating the two: `touch` the importing file with no `.pyc` anywhere and the
error appears; delete the `.pyc` alone and leave the importing file untouched
and it stays green.

**The mechanism, both halves.** Neither is a bug on its own:

- isort's `match_sources` resolves first-party by probing the **full dotted
  path** under the `src` roots — `a.b.c` is first-party only if `[SRC]/a/b/c`
  is a directory or `[SRC]/a/b/c.py` or `.pyi` exists. So one file's verdict
  depends on whether a *different* file exists.
- ruff's cache key is the linted file's mtime and mode. It hashes no content
  and references no other path.

Deleting a module therefore invalidates nothing, and every file importing it
replays a verdict it can no longer earn. Upstream has the same root cause open
for `INP001`, which depends on `__init__.py` the same way —
[astral-sh/ruff#5449](https://github.com/astral-sh/ruff/issues/5449), "we don't
invalidate the cache when an `__init__.py` is added or removed". Ruff's
documentation says nothing anywhere about what invalidates a cache entry.

**Only the delete direction is unsafe**, which is what makes it worth a flag
rather than a habit: adding a module is picked up correctly. The cache fails in
exactly the direction that turns the gate green on a tree CI rejects.

**The exposure is the tree outside the package**, which is why it is easy to
miss rather than rare. isort's `detect-same-package` branch settles an
`anesthesia_sim.*` import first-party for any file under `src/anesthesia_sim/`
before the filesystem probe is reached, so `tests/`, `tools/` and `spikes/` are
where a deleted module actually surfaces — and all four files the port left
stale were in those trees.

**Fixed by** `--no-cache` on both `ruff check` lines in the `Makefile`, with
`tools/doc_check.py`'s `check_ruff_cache` holding every `ruff check` recipe
line in that file to the flag so a line added later cannot arrive without it.
`make fix` needed it as much as `make check`: a stale clean verdict makes
`--fix` a no-op, so the target reports nothing to fix and the import ruff would
have rewritten reaches CI unsorted.

**What was considered and refused.**

- `known-first-party = ["anesthesia_sim"]` would work — isort consults
  `known_modules` before probing the filesystem — but treats the instance
  rather than the fault. The fault is that the cache does not track the
  filesystem facts a verdict rests on, so the next rule reading another file
  reintroduces the divergence; it would also silence the sorter on an import of
  a module that is genuinely gone.
- `PYTHONDONTWRITEBYTECODE=1`, which this item originally proposed, is already
  exported at `Makefile:21` and is irrelevant to this defect.
- An exported `RUFF_NO_CACHE` beside it takes `true`/`false` and **rejects `1`
  outright**, so the obvious copy of its neighbour's `:= 1` would fail every
  ruff invocation at argument parsing.
- The formatter keeps its cache: its output depends only on the file in front
  of it, so a stale entry there needs that file to have changed, which is what
  invalidates the entry.

**Cost.** Measured 2026-09-15 over 150 files: `ruff check` 14 ms warm against
41 ms cache-free, so the gate pays 27 ms to stop asking a different question
from CI's.
