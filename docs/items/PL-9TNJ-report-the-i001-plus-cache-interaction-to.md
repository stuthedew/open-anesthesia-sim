---
id: PL-9TNJ
title: "Report the I001-plus-cache interaction to astral-sh/ruff: #5449 has the same root cause open for INP001 only, and PL-QSJM established both halves"
priority: P3
effort: S
status: done
classes: infra
feature: dev-tooling
touches: docs/items
added: 2026-09-15
closed: 2026-09-15
verify: grep -qE 'astral-sh/ruff/issues/5449#issuecomment-[0-9]+' docs/items/PL-9TNJ-*.md
---

**Problem.** Report the `I001`-plus-cache interaction to astral-sh/ruff.
`PL-QSJM` established both halves; upstream has the same root cause open for
`INP001` only.

**Decided 2026-09-15 (project owner).** Comment the reproduction onto
[astral-sh/ruff#5449](https://github.com/astral-sh/ruff/issues/5449) rather
than open a new issue. Confirmed against the live issue the same day: it is
**open**, assigned to `zanieb`, carries **no comments**, and mentions isort,
`I001`, import sorting, first-party classification, `src` roots and
`match_sources` nowhere. So the comment is new information on an issue whose
author has already named this root cause, rather than a duplicate.

**What PL-QSJM established.** Both halves, verified against ruff 0.16.4's own
source rather than taken from a summary:

- `crates/ruff_linter/src/rules/isort/categorize.rs`'s `match_sources` builds
  `let relative_path: PathBuf = name.split('.').collect();` and probes
  `root.join(&relative_path)` as a directory, then `.py`, then `.pyi` — the
  **full dotted path**, so one file's verdict depends on whether a *different*
  file exists.
- `crates/ruff/src/cache.rs`'s `FileCacheKey` holds `file_last_modified` and
  `file_permissions_mode` and nothing else — no content hash, no other path.

`match_sources` sits at branch 7 of `categorize`, after `known_modules` and
after `detect_same_package`, which is why the exposure is the tree *outside*
the package root.

**Why it matters.** If it lands upstream, this project stops carrying
`--no-cache` and the 27 ms with it. If it does not, nothing is lost: `PL-QSJM`
is closed and the gate is correct either way.

**Done when** the comment below is posted and its URL is recorded in this file,
which is what the `verify:` above reads. If the owner changes their mind, drop
this item with that as the `reason` instead.

## The exact steps

This session cannot post it: `astral-sh/ruff` is outside its repository scope,
and it has no write access there — nor should it.

1. Open <https://github.com/astral-sh/ruff/issues/5449>.
2. Paste the comment below into the comment box at the bottom and press
   **Comment**.
3. Copy the new comment's permalink (the **…** menu on the posted comment →
   **Copy link**; it looks like
   `https://github.com/astral-sh/ruff/issues/5449#issuecomment-NNNNNNNNNN`).
4. Paste that URL into this file under a `**Posted.**` line, and close this
   item.

## The comment, as drafted

> Same root cause, reported here for `I001` (isort) rather than `INP001`, since
> a minimal reproduction is short and both halves are visible in the source.
>
> **Why `I001` is exposed to it.** `match_sources` resolves first-party by
> probing the *full dotted path* under the `src` roots — `foo.baz` is
> first-party only if `[SRC]/foo/baz` is a directory or `[SRC]/foo/baz.py` or
> `.pyi` exists. So one file's `I001` verdict depends on whether a **different**
> file exists. Meanwhile the per-file cache key is:
>
> ```rust
> #[derive(CacheKey)]
> pub(crate) struct FileCacheKey {
>     /// Timestamp when the file was last modified before the (cached) check.
>     file_last_modified: FileTime,
>     /// Permissions of the file before the (cached) check.
>     file_permissions_mode: u32,
> }
> ```
>
> — the linted file's mtime and permission bits, and nothing else, and `Cache::get`
> compares only a hash of that. Deleting a
> module therefore invalidates nothing, and every file importing it replays a
> clean verdict it can no longer earn.
>
> **Reproduction**, identical on ruff 0.16.4 and 0.16.7:
>
> ```sh
> cd "$(mktemp -d)"
> mkdir -p src/pkg/app other
> printf '[tool.ruff.lint]\nselect = ["I"]\n' > pyproject.toml
> touch src/pkg/__init__.py src/pkg/app/__init__.py
> echo "A = 1" > src/pkg/app/gone.py
> echo "B = 2" > src/pkg/app/stays.py
> printf 'from pkg.app.gone import A\nfrom pkg.app.stays import B\n' > other/probe.py
>
> ruff check .              # All checks passed!
> rm src/pkg/app/gone.py
> ruff check .              # All checks passed!   <-- stale
> ruff check --no-cache .   # I001 on other/probe.py
> ```
>
> With the cache bypassed the third run reports:
>
> ```
> I001 [*] Import block is un-sorted or un-formatted
>  --> other/probe.py:1:1
> ```
>
> because `pkg.app.gone` no longer resolves and is sorted third-party while its
> neighbour stays first-party.
>
> **It is asymmetric, in the direction that hurts.** Deleting a module goes
> stale; *adding* one is picked up. So the cached answer is wrong precisely when
> it says "clean" about a tree a fresh checkout rejects — which is how it
> surfaces in practice: a local `ruff check` passes, CI fails on the same
> commit, and `rm -rf .ruff_cache` is the only thing that reconciles them.
>
> One wrinkle that makes it easy to misattribute: `touch`ing the *importing*
> file alone unmasks the diagnostic, with no cache flag, because any edit to it
> moves the mtime the key reads. We first blamed a stale `__pycache__` for
> exactly that reason — the experiment that "confirmed" it had also rewritten
> the importing file.
>
> Happy to split this into its own issue if you would rather keep #5449 to
> `INP001`.

**Posted 2026-09-15** by the project owner:
<https://github.com/astral-sh/ruff/issues/5449#issuecomment-5687726691>

**Confirmed live on the latest release before posting.** The reproduction was
re-run verbatim against **ruff 0.16.7**, the current release, as well as the
0.16.4 this project pins, and behaves identically: run 2 replays a clean
verdict on a tree whose module has been deleted, run 3 reports the `I001` with
`--no-cache`. So the defect is live upstream rather than already fixed, which
is what made the report worth making. Both source facts were read from ruff's
own tree at both tags rather than taken from a summary: `FileCacheKey` holds
`file_last_modified` and `file_permissions_mode` and nothing else, and
`Cache::get` hashes exactly that and compares it, consulting neither file
contents nor any other path.

**Not independently confirmed from this container**, and recorded as such: the
issue page's comment section returns a load error to the fetcher available
here, and `api.github.com` answers 403 because `astral-sh/ruff` is outside this
session's repository scope. The URL above is the permalink the project owner
copied from the comment they posted. Attaching a third-party repository to the
session to verify one comment was judged disproportionate.

**Two possibly-related issues, surfaced but not verified** (a search turned
them up; neither was read against its page, so check before citing either):
`astral-sh/ruff#21647`, reported as ruff finding problems in CI but not
locally, and `astral-sh/ruff#20553`, on inconsistent first-party resolution
between a file inside the package and one outside it. They were deliberately
left out of the comment above rather than cited unverified.
